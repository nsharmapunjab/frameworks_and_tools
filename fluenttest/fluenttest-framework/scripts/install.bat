@echo off
REM FluentTest Installation Script for Windows v2.0
REM ===============================================

echo Installing FluentTest Framework v2.0...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo Python found

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Install Appium (if npm is available)
npm --version >nul 2>&1
if not errorlevel 1 (
    echo Installing Appium...
    npm install -g appium@next
    appium driver install uiautomator2
) else (
    echo Node.js not found. Please install Appium manually:
    echo 1. Install Node.js from https://nodejs.org
    echo 2. Run: npm install -g appium@next
    echo 3. Run: appium driver install uiautomator2
)

REM Install FluentTest
echo Installing FluentTest...
pip install -e .

REM Create directories
mkdir screenshots 2>nul
mkdir logs 2>nul
mkdir reports 2>nul

echo.
echo FluentTest installation complete!
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Configure Android device/emulator
echo 3. Start Appium: appium
echo 4. Run example: python examples\basic_example.py
echo.
pause
