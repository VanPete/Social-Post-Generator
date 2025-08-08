@echo off
cls
echo ===============================================
echo    Adcellerant Social Caption Generator
echo ===============================================
echo.

:: Set working directory
cd /d "%~dp0"
echo [1/6] Setting working directory...
echo Working directory: %cd%
echo.

:: Check if virtual environment exists
echo [2/6] Checking virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ ERROR: Virtual environment not found!
    echo.
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Virtual environment found
echo.

:: Check if .env file exists
echo [3/6] Checking environment file...
if not exist ".env" (
    echo ❌ ERROR: .env file not found!
    echo.
    echo Please create .env file with:
    echo OPENAI_API_KEY=your_api_key_here
    echo APP_PASSWORD=Jax2021
    pause
    exit /b 1
)
echo ✅ .env file found
echo.

:: Check if main.py exists
echo [4/6] Checking main application file...
if not exist "main.py" (
    echo ❌ ERROR: main.py not found!
    pause
    exit /b 1
)
echo ✅ main.py found
echo.

:: Install/update dependencies
echo [5/6] Installing dependencies...
echo This may take a moment...
.venv\Scripts\python.exe -m pip install --upgrade pip > nul 2>&1
.venv\Scripts\python.exe -m pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo Trying manual installation...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencies ready
echo.

:: Start the application
echo [6/6] Starting Streamlit application...
echo.
echo ===============================================
echo   🚀 LAUNCHING APPLICATION...
echo ===============================================
echo.
echo ➤ Application will open in your default browser
echo ➤ Login password: Jax2021
echo ➤ Press Ctrl+C to stop the application
echo ➤ Close this window to stop the application
echo.

.venv\Scripts\python.exe -m streamlit run main.py --server.headless false --server.port 8501 --server.address localhost

echo.
echo ===============================================
echo   Application stopped
echo ===============================================
pause
