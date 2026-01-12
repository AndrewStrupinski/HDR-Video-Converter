#!/bin/bash
# HDR Converter - One-Click Launcher
# Double-click this file to start the app

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "Starting HDR Converter..."

# Use Homebrew Python if available
if [ -f "/opt/homebrew/bin/python3.12" ]; then
    PYTHON="/opt/homebrew/bin/python3.12"
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PYTHON="/opt/homebrew/bin/python3"
else
    PYTHON="python3"
fi

echo "Using Python: $PYTHON"

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    osascript -e 'display dialog "FFmpeg not found!\n\nInstall with:\nbrew install ffmpeg\n\nThen try again." buttons {"OK"} default button "OK" with icon stop with title "HDR Converter"'
    exit 1
fi

# Run the web app (opens in browser - no Tk needed!)
echo "Opening in your browser..."
$PYTHON web_app.py
