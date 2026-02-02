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
echo.

:: Step 1: Check Python version
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found!
    echo.
    echo Please install Python 3.10 or newer from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found, checking version...

:: Get and display Python version directly
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo Detected: Python %PYTHON_VERSION%
echo + Python version check passed
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
    echo Installing dependencies - this may take a few minutes...
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
echo.

:: Start server in a NEW visible window (not background)
start "Whisper Hindi2Hinglish Server" python web_server.py

:: Give server time to initialize
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Verify server is actually running and responding
echo Checking server health...

:: Use PowerShell for better compatibility (curl may not be available on older Windows)
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/health' -TimeoutSec 3 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo.
    echo X Server failed to start or not responding!
    echo.
    echo Possible causes:
    echo   - Port 5000 is already in use by another program
    echo   - Server crashed - check the server window for errors
    echo   - Firewall blocking localhost connections
    echo.
    echo Troubleshooting:
    echo   1. Close any programs using port 5000
    echo   2. Check the "Whisper Hindi2Hinglish Server" window for errors
    echo   3. Try running: python web_server.py --port 5001
    echo.
    pause
    exit /b 1
)

echo + Server started successfully
echo.

:: Step 5: Open browser
echo [5/5] Opening web interface...
start http://localhost:5000
echo + Browser opened
echo.

:: Success message
echo ========================================================
echo   SUCCESS! Server is running
echo ========================================================
echo.
echo Server window: "Whisper Hindi2Hinglish Server"
echo Web interface: http://localhost:5000
echo.
echo IMPORTANT:
echo   - Keep BOTH windows open while using the app
echo   - The server window shows what's happening
echo   - Browser should have opened automatically
echo.
echo If browser didn't open, manually go to:
echo   http://localhost:5000
echo.
echo To stop: Close the server window or press Ctrl+C there
echo.
echo ========================================================
echo Press any key to open browser again, or close this window
pause >nul

:: Re-open browser if needed
start http://localhost:5000
echo.
echo Script completed!
pause
exit /b 0

:: ============================================================================
:: Subroutine: Check Python Version
:: ============================================================================
:CheckPythonVersion
echo [DEBUG] Entering CheckPythonVersion subroutine...
setlocal enabledelayedexpansion
set "PYTHON_VERSION="
set "PYTHON_MAJOR=0"
set "PYTHON_MINOR=0"

:: Get version string
echo [DEBUG] Getting Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [DEBUG] Python version detected: !PYTHON_VERSION!

if not defined PYTHON_VERSION (
    echo.
    echo X Could not detect Python version
    echo.
    echo Please ensure Python 3.10+ is installed correctly.
    pause
    exit /b 1
)

echo + Python found: Python !PYTHON_VERSION!

:: Extract major and minor version numbers
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set "PYTHON_MAJOR=%%a"
    set "PYTHON_MINOR=%%b"
)

:: Validate version is 3.10+
if !PYTHON_MAJOR! LSS 3 (
    echo.
    echo X Python version too old: !PYTHON_VERSION!
    echo   Required: Python 3.10 or newer
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

if !PYTHON_MAJOR! EQU 3 if !PYTHON_MINOR! LSS 10 (
    echo.
    echo X Python version too old: !PYTHON_VERSION!
    echo   Required: Python 3.10 or newer
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

endlocal
exit /b 0
