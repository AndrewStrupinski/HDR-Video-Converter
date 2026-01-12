#!/usr/bin/env python3
"""
HDR Video Converter - Command Line Tool

Usage:
    python3 convert_hdr.py /path/to/video.mp4
    
Or drag a video file onto this script in Finder.
"""

import sys
import os
from pathlib import Path

# Add script directory to path
sys.path.insert(0, str(Path(__file__).parent))

from converter import HDRConverter, ConversionError, SUPPORTED_EXTENSIONS


def show_notification(title, message):
    """Show macOS notification."""
    os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')


def show_dialog(message, title="HDR Converter"):
    """Show macOS dialog."""
    os.system(f'''osascript -e 'display dialog "{message}" buttons {{"OK"}} default button "OK" with title "{title}"' ''')


def progress_callback(percent, message):
    """Print progress to terminal."""
    bar_length = 30
    filled = int(bar_length * percent / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r  [{bar}] {percent:.1f}% - {message}', end='', flush=True)


def convert_file(input_path):
    """Convert a single file to HDR."""
    input_path = Path(input_path)
    
    print(f"\n🎬 HDR Video Converter")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Input: {input_path.name}")
    
    # Validate
    if not input_path.exists():
        show_dialog(f"File not found:\\n{input_path}")
        return False
    
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        show_dialog(f"Unsupported format: {input_path.suffix}\\n\\nSupported: {', '.join(SUPPORTED_EXTENSIONS)}")
        return False
    
    # Convert
    try:
        converter = HDRConverter(progress_callback=progress_callback)
        output_path = converter.convert(str(input_path))
        
        print(f"\n\n✅ Conversion complete!")
        print(f"  Output: {Path(output_path).name}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Show notification and reveal in Finder
        show_notification("HDR Converter", f"Done: {Path(output_path).name}")
        os.system(f'open -R "{output_path}"')
        return True
        
    except ConversionError as e:
        print(f"\n\n❌ Error: {e}")
        show_dialog(f"Conversion failed:\\n{str(e)[:100]}")
        return False
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        show_dialog(f"Unexpected error:\\n{str(e)[:100]}")
        return False


def main():
    if len(sys.argv) < 2:
        print("\n🎬 HDR Video Converter")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  Usage: Drag a video file onto this script")
        print("  Or run: python3 convert_hdr.py /path/to/video.mp4")
        print(f"  Supported: {', '.join(sorted(ext.upper()[1:] for ext in SUPPORTED_EXTENSIONS))}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # Keep window open
        input("Press Enter to exit...")
        return
    
    # Process each file argument
    for file_path in sys.argv[1:]:
        convert_file(file_path)
    
    # Keep terminal open briefly so user can see result
    import time
    time.sleep(3)


if __name__ == '__main__':
    main()
