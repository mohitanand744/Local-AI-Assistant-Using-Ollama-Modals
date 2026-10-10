@echo off
title Coding Beast
color a

echo ========================================
echo        STARTING CODING BEAST...
echo ========================================

:: Navigate to the directory where this script is located
cd /d "%~dp0"

:: Activate the virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found at .venv\Scripts\activate.bat
    pause
    exit /b 1
)

:: Run the main application
python coding_beast.py

echo.
echo Coding Beast has stopped.
pause
