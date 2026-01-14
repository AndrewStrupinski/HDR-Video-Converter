<div align="center">

# 🎬 HDR Video Converter

**Convert any video to HDR/HLG format for iPhone and Apple devices**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-10.13+-blue.svg)](https://github.com/AndrewStrupinski/HDR-HLG-converter/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10+-blue.svg)](https://github.com/AndrewStrupinski/HDR-HLG-converter/releases/latest)

---

### ⬇️ Download

| Platform | Download |
|:--------:|:--------:|
| **Mac** | [**📥 Download for macOS**](https://github.com/AndrewStrupinski/HDR-HLG-converter/releases/latest/download/HDR-Converter-macOS.dmg) |
| **Windows** | [**📥 Download for Windows**](https://github.com/AndrewStrupinski/HDR-HLG-converter/releases/latest/download/HDR-Converter-Windows.zip) |

*Or [view all releases](https://github.com/AndrewStrupinski/HDR-HLG-converter/releases)*

---

</div>

## ✨ What It Does

- Converts regular videos to **HDR/HLG format**
- Your iPhone will show the **HDR badge** ✓
- Videos look more vibrant on HDR displays
- Simple drag-and-drop or web interface

<div align="center">

![HDR Badge Example](https://img.shields.io/badge/📱_iPhone_Shows-HDR_Badge-success?style=for-the-badge)

</div>

---

## 🚀 Quick Start

### Mac Users

1. **Download** the `.dmg` file from the button above
2. **Open** the DMG and drag the app to Applications
3. **Right-click** the app → Open (first time only, to bypass Gatekeeper)
4. **Select a video** and click Convert!

### Windows Users

1. **Download** the `.zip` file from the button above
2. **Extract** the zip file
3. **Run** `HDR Converter.exe`
4. **Select a video** and click Convert!

---

## 📍 Where Are My Converted Videos?

Converted files are saved to:

```
📁 Movies → HDR Converted
```

*(On Mac: ~/Movies/HDR Converted)*

---

## 🤔 Troubleshooting

<details>
<summary><b>"App can't be opened" on Mac</b></summary>

Right-click the app → click **Open** → click **Open** again in the dialog.
This is a one-time thing for apps downloaded from the internet.
</details>

<details>
<summary><b>Video doesn't show HDR badge on iPhone</b></summary>

- Make sure you're transferring via **AirDrop** (not iCloud)
- The video should be at least a few seconds long
- The HDR badge appears when you play the video
</details>

<details>
<summary><b>Conversion is slow</b></summary>

HDR encoding is CPU-intensive. A 1-minute video takes about 15-30 seconds depending on your computer.
</details>

---

## 💝 Support This Project

If you find this useful, consider supporting development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/andrewstrupinski)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?style=for-the-badge&logo=paypal)](https://paypal.me/andrewstrupinski)

---

## 🛠️ For Developers

<details>
<summary><b>Running from Source</b></summary>

### Requirements
- Python 3.9+
- FFmpeg with libx265

### Install
```bash
# Clone the repo
git clone https://github.com/AndrewStrupinski/HDR-HLG-converter.git
cd HDR-HLG-converter

# Install FFmpeg (macOS)
brew install ffmpeg

# Run the web interface
python3 web_app.py
```

### Command Line
```bash
python3 convert_hdr.py /path/to/video.mp4
```

</details>

<details>
<summary><b>How It Works</b></summary>

The converter uses FFmpeg's `zscale` filter to convert SDR colorspace to HDR:

- **Color Primaries**: BT.2020 (wide color gamut)
- **Transfer Function**: HLG (Hybrid Log-Gamma)
- **Mastering Display**: Standard HDR10 metadata
- **Encoder**: x265 at 35 Mbps

This produces files that Apple devices correctly identify as HDR content.
</details>

<details>
<summary><b>Building Releases</b></summary>

Releases are automatically built via GitHub Actions when you push a version tag:

```bash
git tag v1.x.x
git push origin v1.x.x
```

This creates macOS DMG and Windows ZIP automatically.
</details>

---

## 📄 License

MIT License - Use it however you want!

---

## 🙏 Credits

- [FFmpeg](https://ffmpeg.org/) for video processing
- [x265](https://x265.org/) for HEVC encoding  
- [Claude AI](https://anthropic.com/) for development assistance

---

<div align="center">

**Made with ❤️ by [Andrew Strupinski](https://github.com/AndrewStrupinski)**

</div>
