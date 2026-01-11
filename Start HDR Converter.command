#!/bin/bash
# HDR Converter - One-Click Launcher
# Double-click this file to start the app

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "First run - setting up environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q tkinterdnd2
else
    source .venv/bin/activate
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    osascript -e 'display dialog "FFmpeg not found!\n\nInstall with:\nbrew install ffmpeg" buttons {"OK"} default button "OK" with icon stop with title "HDR Converter"'
    exit 1
fi

# Run the app
python main.py
