# HDR Video Converter

Convert standard videos to HDR/HLG format that displays with the HDR badge on iPhone and Apple devices.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 🎬 **SDR to HDR Conversion** - Converts standard videos to HDR using the HLG (Hybrid Log-Gamma) format
- 📱 **iPhone Compatible** - Properly tagged so iPhone shows the HDR badge
- 🖥️ **Multiple Interfaces** - Web UI, drag-and-drop app, or command line
- 📂 **Organized Output** - Saves to `~/Movies/HDR Converted/` for easy access
- ⚡ **High Quality** - 35 Mbps encoding with full HDR metadata

## Quick Start

### Option 1: Web Interface (Recommended)
1. Double-click `Start HDR Converter.command`
2. Your browser opens automatically
3. Select a video file and click "Convert to HDR"
4. Find your converted file in `~/Movies/HDR Converted/`

### Option 2: Drag and Drop
1. Drag any video file onto `Convert to HDR.app`
2. Wait for conversion to complete
3. Output folder opens automatically

### Option 3: Command Line
```bash
python3.12 convert_hdr.py /path/to/video.mp4
```

## Requirements

- **macOS** 10.13+ or **Windows** 10+
- **FFmpeg** with libx265 and zscale support
- **Python** 3.9+ (for running from source)

### Installing Dependencies (macOS)

The launcher will attempt to install these automatically, or you can run:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 ffmpeg
```

## How It Works

The converter uses FFmpeg's `zscale` filter to properly convert SDR colorspace to HDR:

- **Color Primaries**: BT.2020 (wide color gamut)
- **Transfer Function**: ARIB STD-B67 (HLG)
- **Color Matrix**: BT.2020 non-constant luminance
- **Mastering Display**: Standard HDR metadata
- **Content Light Level**: 1000 nits max

This produces video files that iPhone and other Apple devices correctly recognize as HDR content.

## Output

Converted files are saved to:
```
~/Movies/HDR Converted/
```

Files are named with `_HDR` suffix: `MyVideo.mp4` → `MyVideo_HDR.mp4`

## Building from Source

### Prerequisites
```bash
pip install -r requirements.txt
```

### Create Standalone App (macOS)
```bash
pyinstaller build.spec
```

The app will be in `dist/HDR Converter.app`

## GitHub Releases

Releases are automatically built when you push a version tag:

```bash
git tag v1.x.x
git push origin v1.x.x
```

This creates:
- `HDR-Converter-macOS.dmg` - macOS app bundle
- `HDR-Converter-Windows.zip` - Windows executable

## Project Structure

```
HDR-HLG-converter/
├── converter.py          # Core conversion logic
├── convert_hdr.py        # CLI tool
├── web_app.py           # Web interface
├── main.py              # GUI app (Tkinter)
├── Start HDR Converter.command  # macOS launcher
├── Convert to HDR.app   # Drag-and-drop app
├── build.spec           # PyInstaller config
├── icon.icns            # macOS app icon
├── icon.ico             # Windows app icon
└── .github/workflows/   # GitHub Actions
```

## Supported Formats

**Input**: MP4, MOV, MKV, AVI, WebM, M4V, WMV, FLV

**Output**: MP4 (HEVC/H.265, AAC audio)

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg: `brew install ffmpeg`

### "Python not found"  
Install Python: `brew install python@3.12`

### Video doesn't show HDR badge on iPhone
- Make sure you're using AirDrop (not iCloud)
- The video should be at least a few seconds long
- Try playing the video - the HDR badge appears during playback

### Port already in use
Stop the existing server: `lsof -ti:8765 | xargs kill`

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

- FFmpeg for video processing
- x265 for HEVC encoding
- Apple's HLG specification for HDR format

## Contributing

Pull requests welcome! Please open an issue first to discuss major changes.
