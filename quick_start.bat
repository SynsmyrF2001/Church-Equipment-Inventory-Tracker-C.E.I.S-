@echo off
REM Church Equipment Inventory System - Quick Start Script for Windows
REM This script helps you get the application running quickly on Windows

echo 🚀 Church Equipment Inventory System - Quick Start
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
if exist "uv.exe" (
    echo Using uv package manager...
    uv sync
) else (
    echo Using pip package manager...
    pip install -r requirements.txt
)

REM Set up environment variables
if not exist ".env" (
    echo ⚙️  Creating .env file...
    python -c "import secrets; print('SESSION_SECRET=' + secrets.token_hex(32))" > .env
    echo DATABASE_URL=sqlite:///church_inventory.db >> .env
    echo FLASK_ENV=development >> .env
    echo DEBUG=True >> .env
    echo ✅ Created .env file with secure session secret
) else (
    echo ✅ .env file already exists
)

REM Initialize database
echo 🗄️  Initializing database...
python -c "from app import app, db; app.app_context().push(); db.create_all()"
if errorlevel 1 (
    echo ❌ Failed to initialize database. Please check your configuration.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete! Starting the application...
echo 📱 The application will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

pause 