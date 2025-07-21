@echo off
echo Target.com Product Scraper
echo ========================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing/updating requirements...
pip install -r requirements.txt

REM Run the scraper
if "%1"=="" (
    echo No search term provided. Starting interactive mode...
    python target_search_cli.py
) else (
    echo Searching for: %*
    python target_search_cli.py %*
)

pause
