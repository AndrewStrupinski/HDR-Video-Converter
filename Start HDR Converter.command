#!/bin/bash
# HDR Converter - One-Click Launcher

cd "$(dirname "$0")"

# Add Homebrew to PATH for the session
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "🎬 HDR Video Converter"
echo "Starting web interface..."

/opt/homebrew/bin/python3.12 web_app.py
