# HDR Converter iOS

A native iOS app that converts standard videos to HDR/HLG format, displaying with the HDR badge on iPhone.

## Setup Instructions

### 1. Create Xcode Project

1. Open Xcode
2. File → New → Project
3. Choose **iOS → App**
4. Settings:
   - Product Name: `HDR Converter`
   - Team: (Your Apple ID)
   - Organization Identifier: `com.yourname`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Minimum Deployment: **iOS 15.0**

### 2. Add Source Files

Copy the contents of `HDRConverterApp.swift` and split into these files in your Xcode project:

| File | Purpose |
|------|---------|
| `HDRConverterApp.swift` | App entry point |
| `ContentView.swift` | Main UI |
| `HDRConverterViewModel.swift` | Business logic |
| `HDRConverter.swift` | Video conversion |

### 3. Configure Info.plist

Add these keys to your `Info.plist`:

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>HDR Converter needs access to your photos to select and save videos.</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>HDR Converter needs permission to save converted HDR videos to your Photos.</string>
```

### 4. Build & Run

1. Connect your iPhone or use Simulator
2. Select your device in Xcode
3. Press **⌘R** to build and run

## Requirements

- Xcode 14+
- iOS 15.0+ device
- Apple Developer account (free for testing on your own device)

## How It Works

The app uses Apple's native frameworks:

- **PhotosUI** - Video picker from Photos library
- **AVFoundation** - Video reading and composition  
- **VideoToolbox** - HEVC encoding with HLG transfer function
- **Photos** - Save converted video back to library

### HDR Settings Applied:

- Color Primaries: BT.2020
- Transfer Function: HLG (Hybrid Log-Gamma)
- Color Matrix: BT.2020

## Limitations

- Uses Apple's built-in encoder (less control than FFmpeg)
- Processing time depends on video length and device
- Some older devices may not support all HDR features

## License

MIT License - see parent project LICENSE
