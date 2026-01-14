# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for HDR Video Converter.

Build commands:
  macOS:   pyinstaller build.spec
  Windows: pyinstaller build.spec

The resulting executable will be in dist/
"""

import sys
from pathlib import Path

# Application info
APP_NAME = 'HDR Converter'
MAIN_SCRIPT = 'main.py'

# Detect platform
is_macos = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

# FFmpeg binary path (if bundled)
ffmpeg_binaries = []
ffmpeg_dir = Path('ffmpeg')

if ffmpeg_dir.exists():
    if is_macos:
        if (ffmpeg_dir / 'ffmpeg').exists():
            ffmpeg_binaries.append((str(ffmpeg_dir / 'ffmpeg'), 'ffmpeg'))
        if (ffmpeg_dir / 'ffprobe').exists():
            ffmpeg_binaries.append((str(ffmpeg_dir / 'ffprobe'), 'ffmpeg'))
    elif is_windows:
        if (ffmpeg_dir / 'ffmpeg.exe').exists():
            ffmpeg_binaries.append((str(ffmpeg_dir / 'ffmpeg.exe'), 'ffmpeg'))
        if (ffmpeg_dir / 'ffprobe.exe').exists():
            ffmpeg_binaries.append((str(ffmpeg_dir / 'ffprobe.exe'), 'ffmpeg'))

# Analysis
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=ffmpeg_binaries,
    datas=[],
    hiddenimports=['tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Package
pyz = PYZ(a.pure)

# Determine icon file
icon_file = None
if is_macos and Path('icon.icns').exists():
    icon_file = 'icon.icns'
elif is_windows and Path('icon.ico').exists():
    icon_file = 'icon.ico'

# Executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no terminal)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# macOS App Bundle
if is_macos:
    # Try to get version from VERSION file or environment
    import os
    version = os.environ.get('APP_VERSION', '1.0.0')
    if version.startswith('v'):
        version = version[1:]  # Remove 'v' prefix
    
    app = BUNDLE(
        exe,
        name=f'{APP_NAME}.app',
        icon='icon.icns' if Path('icon.icns').exists() else None,
        bundle_identifier='com.andrewstrupinski.hdrconverter',
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': version,
            'CFBundleShortVersionString': version,
            'CFBundleGetInfoString': f'HDR Video Converter {version} - https://github.com/AndrewStrupinski/HDR-Video-Converter',
            'NSHumanReadableCopyright': 'Copyright © 2026 Andrew Strupinski. MIT License.',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
