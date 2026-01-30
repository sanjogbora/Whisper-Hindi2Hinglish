@echo off
title Whisper Hindi2Hinglish - Video to SRT Converter
color 0A

:: Visual welcome
echo.
echo ========================================================
echo   Whisper Hindi2Hinglish - Video to SRT Converter
echo   Starting up...
echo ========================================================
echo.

:: Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo + Python found: %PYTHON_VERSION%
)
echo.

:: Step 2: Check FFmpeg
echo [2/5] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo X FFmpeg not found!
    echo.
    echo Attempting to install FFmpeg via winget...
    winget install --id Gyan.FFmpeg -e --silent
    if errorlevel 1 (
        echo.
        echo Auto-install failed. Please install manually from:
        echo https://ffmpeg.org/download.html
        echo.
        echo After installation, restart this launcher.
        pause
        exit /b 1
    ) else (
        echo + FFmpeg installed successfully
        echo.
        echo Please restart this launcher for FFmpeg to be recognized.
        pause
        exit /b 0
    )
) else (
    echo + FFmpeg found
)
echo.

:: Step 3: Check dependencies
echo [3/5] Checking Python dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo X Dependencies not installed
    echo.
    echo Installing dependencies (this may take a few minutes)...
    echo Please wait...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo X Failed to install dependencies
        echo.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    echo.
    echo + Dependencies installed successfully
) else (
    echo + Dependencies already installed
)
echo.

:: Step 4: Start server
echo [4/5] Starting web server...
start /B python web_server.py
timeout /t 3 /nobreak >nul
echo + Server started
echo.

:: Step 5: Open browser
echo [5/5] Opening web interface...
start http://localhost:5000
echo + Browser opened
echo.

:: Success message
echo ========================================================
echo   Server running at http://localhost:5000
echo   Browser should open automatically
echo   Keep this window open while using the app
echo ========================================================
echo.
echo Press Ctrl+C to stop the server, or just close this window
echo.
pause
