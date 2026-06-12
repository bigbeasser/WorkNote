@echo off
echo ============================================
echo   CTRM Knowledge Base - MkDocs Server
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

pip show mkdocs-material >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies ...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [ERROR] Install failed. Run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo [OK] Starting server...
echo [OK] Open browser: http://localhost:8899
echo [OK] Press Ctrl+C to stop
echo.

cd /d "%~dp0"
mkdocs serve --dev-addr localhost:8899
