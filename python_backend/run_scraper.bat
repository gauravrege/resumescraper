@echo off
title "Resume Scraper and Category Segregator"
color 0B
cls

echo =====================================================================
echo               RESUME SCRAPER AND EXCEL EXPORTER
echo =====================================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Setting up .venv...
    py -m venv .venv
    echo [*] Installing required packages...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: Run the Python scraper
echo [*] Starting resume extraction...
echo.
.\.venv\Scripts\python.exe main.py --open

echo.
echo =====================================================================
echo Execution finished. Press any key to exit...
echo =====================================================================
pause >nul
