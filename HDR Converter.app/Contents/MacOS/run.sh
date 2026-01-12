#!/bin/bash
# HDR Converter - Droplet Runner

# Get the directory where this app is located
APP_DIR="$(dirname "$(dirname "$(dirname "$0")")")"
SCRIPT_DIR="$(dirname "$APP_DIR")"

# Use Homebrew Python
if [ -f "/opt/homebrew/bin/python3.12" ]; then
    PYTHON="/opt/homebrew/bin/python3.12"
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PYTHON="/opt/homebrew/bin/python3"
else
    PYTHON="python3"
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    osascript -e 'display dialog "FFmpeg not found!\n\nInstall with:\nbrew install ffmpeg" buttons {"OK"} default button "OK" with icon stop with title "HDR Converter"'
    exit 1
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run converter with all arguments (dropped files)
if [ $# -eq 0 ]; then
    # No files dropped - show info
    osascript -e 'display dialog "Drag a video file onto this app to convert it to HDR.\n\nSupported: MP4, MOV, MKV, AVI, WebM" buttons {"OK"} default button "OK" with title "HDR Converter"'
else
    # Open Terminal and run conversion
    osascript -e "tell application \"Terminal\"
        activate
        do script \"cd '$SCRIPT_DIR' && '$PYTHON' convert_hdr.py $@\"
    end tell"
fi
