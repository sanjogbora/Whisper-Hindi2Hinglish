#!/bin/bash

# Change to script directory
cd "$(dirname "$0")"

clear
echo ""
echo "========================================================"
echo "  Whisper Hindi2Hinglish - Video to SRT Converter"
echo "  Starting up..."
echo "========================================================"
echo ""

# Step 1: Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python not found!"
    echo ""
    echo "Please install Python from: https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ Python found: $PYTHON_VERSION"
echo ""

# Step 2: Check FFmpeg
echo "[2/5] Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "✗ FFmpeg not found!"
    echo ""
    echo "Attempting to install FFmpeg via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
        if [ $? -eq 0 ]; then
            echo "✓ FFmpeg installed successfully"
        else
            echo "✗ Auto-install failed"
            echo ""
            echo "Please install FFmpeg manually:"
            echo "https://ffmpeg.org/download.html"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
    else
        echo "✗ Homebrew not installed"
        echo ""
        echo "Please install Homebrew first: https://brew.sh"
        echo "Then run: brew install ffmpeg"
        echo ""
        echo "Or install FFmpeg manually: https://ffmpeg.org/download.html"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "✓ FFmpeg found"
fi
echo ""

# Step 3: Check dependencies
echo "[3/5] Checking Python dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Dependencies not installed"
    echo ""
    echo "Installing dependencies (this may take a few minutes)..."
    echo "Please wait..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Dependencies installed successfully"
    else
        echo ""
        echo "✗ Failed to install dependencies"
        echo ""
        echo "Please check your internet connection and try again."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Step 4: Start server
echo "[4/5] Starting web server..."
python3 web_server.py &
SERVER_PID=$!
sleep 3
echo "✓ Server started (PID: $SERVER_PID)"
echo ""

# Step 5: Open browser
echo "[5/5] Opening web interface..."
open http://localhost:5000
echo "✓ Browser opened"
echo ""

# Success message
echo "========================================================"
echo "  🎉 Server running at http://localhost:5000"
echo "  Browser should open automatically"
echo "  Keep this terminal open while using the app"
echo "========================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; echo 'Server stopped. Goodbye!'; exit" INT TERM
wait $SERVER_PID
