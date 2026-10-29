$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend\backend"
$venvPath = Join-Path $backendRoot ".venv-sync"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"
$envPath = Join-Path $backendRoot ".env"
$sqlPath = Join-Path $projectRoot "setup_database.sql"

Write-Host "Sudarshan Chakra setup" -ForegroundColor Cyan

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonLauncher) { throw "Python Launcher was not found. Install Python 3.11 first." }

if (-not (Test-Path $pythonPath)) {
    & py -3.11 -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "Python 3.11 is required to create the environment." }
}

& $pythonPath -m pip install -r (Join-Path $backendRoot "requirements-py311.txt")
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

$mysqlCandidates = @(
    (Get-Command mysql.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"
) | Where-Object { $_ -and (Test-Path $_) }
$mysqlPath = $mysqlCandidates | Select-Object -First 1
if (-not $mysqlPath) { throw "mysql.exe was not found. Install MySQL Server first." }

$mysqlUser = Read-Host "MySQL username [root]"
if ([string]::IsNullOrWhiteSpace($mysqlUser)) { $mysqlUser = "root" }
$mysqlHost = Read-Host "MySQL host [127.0.0.1]"
if ([string]::IsNullOrWhiteSpace($mysqlHost)) { $mysqlHost = "127.0.0.1" }
$mysqlPort = Read-Host "MySQL port [3306]"
if ([string]::IsNullOrWhiteSpace($mysqlPort)) { $mysqlPort = "3306" }
$securePassword = Read-Host "MySQL password" -AsSecureString
$passwordPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$mysqlPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPtr)
[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPtr)

$encodedPassword = [Uri]::EscapeDataString($mysqlPassword)
$databaseUrl = "mysql+pymysql://$mysqlUser`:$encodedPassword@$mysqlHost`:$mysqlPort/sudarshan_chakra"

if (Test-Path $envPath) {
    $envLines = Get-Content $envPath | Where-Object { $_ -notmatch '^DATABASE_URL=' }
    @("DATABASE_URL=$databaseUrl") + $envLines | Set-Content $envPath
} else {
    $jwtSecret = & $pythonPath -c "import secrets; print(secrets.token_urlsafe(48), end='')"
    $fernetKey = & $pythonPath -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode(), end='')"
    @(
        "DATABASE_URL=$databaseUrl"
        "JWT_SECRET_KEY=$jwtSecret"
        "FERNET_KEY=$fernetKey"
        "STORAGE_ROOT=storage"
        "MAX_UPLOAD_SIZE_BYTES=26214400"
    ) | Set-Content $envPath
}

Get-Content $sqlPath -Raw | & $mysqlPath -u $mysqlUser "--password=$mysqlPassword" -h $mysqlHost -P $mysqlPort
if ($LASTEXITCODE -ne 0) { throw "MySQL authentication or database setup failed." }

Push-Location $backendRoot
try {
    & $pythonPath -m app.db.migrate
    if ($LASTEXITCODE -ne 0) { throw "Database table migration failed." }
} finally {
    Pop-Location
}

Write-Host "Setup complete. Starting the application..." -ForegroundColor Green
& (Join-Path $projectRoot "start_sudarshan.bat")
