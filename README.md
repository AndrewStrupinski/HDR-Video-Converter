# HDR Video Converter

Convert standard video files to HDR format (HLG) that displays as HDR on iPhones and other Apple devices.

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)

## Features

- 🎬 **Drag-and-drop interface** — Just drop a video file to convert
- 📱 **iPhone HDR compatible** — Output is recognized as HDR on iOS devices
- 🎨 **Dark themed UI** — Modern, clean interface
- 📊 **Progress tracking** — See real-time conversion progress
- 🔧 **Cross-platform** — Works on macOS and Windows

## Download

Get the latest release from the [Releases page](../../releases):
- **macOS**: Download `HDR-Converter-macOS.dmg`
- **Windows**: Download `HDR-Converter-Windows.zip`

## Output Format

The converter produces videos with:
- **Codec**: HEVC (H.265) with Main 10 profile
- **Color Space**: Rec. 2100 HLG (Hybrid Log-Gamma)
- **Container**: MP4 with `hvc1` tag for Apple compatibility
- **Audio**: AAC at 256kbps

## Development Setup

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system

### Installing FFmpeg

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (essentials build)
2. Extract and add to PATH, or place `ffmpeg.exe` and `ffprobe.exe` in a `ffmpeg/` folder

### Running from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/HDR-HLG-converter.git
cd HDR-HLG-converter

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Building Standalone Executables

### Local Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build (creates executable in dist/)
pyinstaller build.spec
```

### Bundling FFmpeg (Optional)

To create a fully standalone app that doesn't require FFmpeg to be installed:

1. Create a `ffmpeg/` directory in the project root
2. Place `ffmpeg` and `ffprobe` binaries inside
3. Build with PyInstaller

**macOS:**
```bash
mkdir -p ffmpeg
# Download from evermeet.cx or copy from Homebrew
cp $(which ffmpeg) ffmpeg/
cp $(which ffprobe) ffmpeg/
pyinstaller build.spec
```

**Windows:**
```powershell
mkdir ffmpeg
# Download essentials from gyan.dev, extract, and copy
copy ffmpeg-*\bin\ffmpeg.exe ffmpeg\
copy ffmpeg-*\bin\ffprobe.exe ffmpeg\
pyinstaller build.spec
```

### Automated Builds

Push a release tag to trigger GitHub Actions, which automatically builds for both platforms:

```bash
git tag v1.0.0
git push origin v1.0.0
# Then create a release on GitHub
```

## Usage

1. **Launch the app** — Double-click the executable or run `python main.py`
2. **Add a video** — Drag a video file onto the window, or click to browse
3. **Wait for conversion** — Progress is shown in real-time
4. **Find your file** — Output is saved as `{original_name}_HDR.mp4` in the same folder

### Supported Input Formats

MP4, MOV, MKV, AVI, WebM, M4V, WMV, FLV

## Technical Details

The conversion applies HLG (Hybrid Log-Gamma) HDR metadata using FFmpeg:

```bash
ffmpeg -i input.mp4 \
  -c:v libx265 \
  -pix_fmt yuv420p10le \
  -color_primaries bt2020 \
  -colorspace bt2020nc \
  -color_trc arib-std-b67 \
  -x265-params "hdr-opt=1:repeat-headers=1:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc" \
  -tag:v hvc1 \
  -c:a aac \
  -b:a 256k \
  output_HDR.mp4
```

> **Note**: This applies HDR metadata to the video stream. It does not perform true SDR-to-HDR tone mapping, which would require more complex processing. The result works well for content that will be displayed on HDR-capable devices.

## Troubleshooting

**"FFmpeg not found" error:**
- Install FFmpeg via Homebrew (macOS) or download from gyan.dev (Windows)
- Or place FFmpeg binaries in the `ffmpeg/` directory

**Conversion is slow:**
- HEVC encoding is CPU-intensive; this is normal
- Consider using smaller test files during development

**Output doesn't show HDR badge on iPhone:**
- Ensure you're viewing in the Photos app (not Files)
- Check that your iPhone supports HDR (iPhone 8 or later)
- Verify the file was transferred properly (AirDrop recommended)

## License

MIT License - See [LICENSE](LICENSE) for details.
