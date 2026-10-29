@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_sudarshan.ps1"
if errorlevel 1 (
    echo Setup failed. Review the message above.
    pause
    exit /b 1
)
exit /b 0
