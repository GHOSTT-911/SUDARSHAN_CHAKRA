@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BACKEND_ROOT=%PROJECT_ROOT%backend\backend"
set "PYTHON=%BACKEND_ROOT%\.venv-sync\Scripts\python.exe"
set "URL=http://127.0.0.1:8000/"

if not exist "%PYTHON%" (
    echo Python environment not found:
    echo %PYTHON%
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$connection = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if (-not $connection) { Start-Process -FilePath '%PYTHON%' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory '%BACKEND_ROOT%' -WindowStyle Minimized }"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ready = $false; for ($i = 0; $i -lt 30; $i++) { try { $response = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/api/v1/health' -TimeoutSec 2; if ($response.StatusCode -eq 200) { $ready = $true; break } } catch {}; Start-Sleep -Milliseconds 500 }; if (-not $ready) { exit 1 }"
if errorlevel 1 (
    echo FastAPI did not become ready. Check the backend environment and MySQL service.
    pause
    exit /b 1
)

start "" "%URL%"
exit /b 0
