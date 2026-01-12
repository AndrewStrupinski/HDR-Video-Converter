#!/bin/bash
# HDR Converter - One-Click Launcher
# Checks for dependencies and starts the web interface

cd "$(dirname "$0")"

echo "🎬 HDR Video Converter"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Add common paths
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Function to show error dialog
show_error() {
    osascript -e "display dialog \"$1\" buttons {\"OK\"} default button \"OK\" with icon stop with title \"HDR Converter\""
}

# Function to show info dialog
show_info() {
    osascript -e "display dialog \"$1\" buttons {\"OK\"} default button \"OK\" with title \"HDR Converter\""
}

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found"
    show_error "Homebrew is required but not installed.

To install, open Terminal and run:
/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"

Then restart this app."
    exit 1
fi
echo "✓ Homebrew found"

# Check for Python 3.12
if ! command -v python3.12 &> /dev/null && [ ! -f "/opt/homebrew/bin/python3.12" ]; then
    echo "❌ Python 3.12 not found"
    echo "Installing Python 3.12..."
    osascript -e 'display notification "Installing Python 3.12..." with title "HDR Converter"'
    brew install python@3.12
    if [ $? -ne 0 ]; then
        show_error "Failed to install Python 3.12.

Please run manually in Terminal:
brew install python@3.12"
        exit 1
    fi
fi
echo "✓ Python found"

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null && [ ! -f "/opt/homebrew/bin/ffmpeg" ]; then
    echo "❌ FFmpeg not found"
    echo "Installing FFmpeg..."
    osascript -e 'display notification "Installing FFmpeg..." with title "HDR Converter"'
    brew install ffmpeg
    if [ $? -ne 0 ]; then
        show_error "Failed to install FFmpeg.

Please run manually in Terminal:
brew install ffmpeg"
        exit 1
    fi
fi
echo "✓ FFmpeg found"

# All dependencies OK
echo ""
echo "Starting web interface..."
echo "Output files will be saved to: ~/Movies/HDR Converted/"
echo ""

# Use the appropriate Python
if [ -f "/opt/homebrew/bin/python3.12" ]; then
    /opt/homebrew/bin/python3.12 web_app.py
elif [ -f "/usr/local/bin/python3.12" ]; then
    /usr/local/bin/python3.12 web_app.py
else
    python3.12 web_app.py
fi
