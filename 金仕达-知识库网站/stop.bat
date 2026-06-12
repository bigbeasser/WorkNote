@echo off
echo Stopping Knowledge Base...
echo.

wmic process where "commandline like '%%mkdocs serve%%' and name='python.exe'" get processid 2>nul | findstr /r "[0-9]" >nul
if errorlevel 1 (
    echo [INFO] Server is not running.
    pause
    exit /b 0
)

for /f %%i in ('wmic process where "commandline like '%%mkdocs serve%%' and name='python.exe'" get processid /value 2^>nul ^| findstr "ProcessId"') do (
    set %%i
)

if defined ProcessId (
    taskkill /PID %ProcessId% /F >nul 2>&1
    echo [OK] Server stopped. (PID: %ProcessId%)
) else (
    echo [INFO] Server is not running.
)

pause
