"""
HDR Video Converter - FFmpeg Wrapper Module

Converts standard video files to HDR format (HLG) for iPhone compatibility.
"""

import os
import re
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Callable, Optional, Tuple


# Supported video extensions
SUPPORTED_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v', '.wmv', '.flv'}


class ConversionError(Exception):
    """Custom exception for conversion errors."""
    pass


class HDRConverter:
    """
    Converts video files to HDR/HLG format using FFmpeg.
    
    The output will be HEVC (H.265) with Main 10 profile and Rec. 2100 HLG
    color space, compatible with iPhone HDR display.
    """
    
    def __init__(self, progress_callback: Optional[Callable[[float, str], None]] = None):
        """
        Initialize the HDR converter.
        
        Args:
            progress_callback: Optional callback function that receives
                               (progress_percent, status_message)
        """
        self.progress_callback = progress_callback
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        self._process: Optional[subprocess.Popen] = None
        self._cancelled = False
    
    def _find_ffmpeg(self) -> str:
        """Find the FFmpeg binary, checking bundled location first."""
        # Check bundled location (for packaged app)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Running as script
            bundle_dir = Path(__file__).parent
        
        # Check for bundled ffmpeg
        bundled_paths = [
            bundle_dir / 'ffmpeg' / 'ffmpeg',
            bundle_dir / 'ffmpeg' / 'ffmpeg.exe',
            bundle_dir / 'ffmpeg',
            bundle_dir / 'ffmpeg.exe',
        ]
        
        for path in bundled_paths:
            if path.exists() and path.is_file():
                return str(path)
        
        # Fall back to system FFmpeg
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return system_ffmpeg
        
        raise ConversionError(
            "FFmpeg not found. Please install FFmpeg or place it in the ffmpeg/ directory.\n"
            "macOS: brew install ffmpeg\n"
            "Windows: Download from https://www.gyan.dev/ffmpeg/builds/"
        )
    
    def _find_ffprobe(self) -> Optional[str]:
        """Find FFprobe binary (optional, for duration detection)."""
        if getattr(sys, 'frozen', False):
            bundle_dir = Path(sys._MEIPASS)
        else:
            bundle_dir = Path(__file__).parent
        
        bundled_paths = [
            bundle_dir / 'ffmpeg' / 'ffprobe',
            bundle_dir / 'ffmpeg' / 'ffprobe.exe',
            bundle_dir / 'ffprobe',
            bundle_dir / 'ffprobe.exe',
        ]
        
        for path in bundled_paths:
            if path.exists() and path.is_file():
                return str(path)
        
        return shutil.which('ffprobe')
    
    def _get_duration(self, input_path: str) -> Optional[float]:
        """Get video duration in seconds using ffprobe."""
        if not self.ffprobe_path:
            return None
        
        try:
            result = subprocess.run(
                [
                    self.ffprobe_path,
                    '-v', 'quiet',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    input_path
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError):
            pass
        return None
    
    def _parse_time(self, time_str: str) -> float:
        """Parse FFmpeg time format (HH:MM:SS.ms) to seconds."""
        match = re.match(r'(\d+):(\d+):(\d+\.?\d*)', time_str)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return 0.0
    
    def _report_progress(self, percent: float, message: str):
        """Report progress to callback if available."""
        if self.progress_callback:
            self.progress_callback(min(100.0, max(0.0, percent)), message)
    
    def validate_input(self, input_path: str) -> Tuple[bool, str]:
        """
        Validate the input file.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(input_path)
        
        if not path.exists():
            return False, f"File not found: {input_path}"
        
        if not path.is_file():
            return False, f"Not a file: {input_path}"
        
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format: {path.suffix}\nSupported: {', '.join(SUPPORTED_EXTENSIONS)}"
        
        return True, ""
    
    def get_output_path(self, input_path: str) -> str:
        """Generate output path with _HDR suffix."""
        path = Path(input_path)
        output_name = f"{path.stem}_HDR.mp4"
        return str(path.parent / output_name)
    
    def cancel(self):
        """Cancel the current conversion."""
        self._cancelled = True
        if self._process:
            self._process.terminate()
    
    def convert(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert video to HDR/HLG format.
        
        Args:
            input_path: Path to the input video file
            output_path: Optional custom output path (default: input_HDR.mp4)
            
        Returns:
            Path to the output file
            
        Raises:
            ConversionError: If conversion fails
        """
        self._cancelled = False
        
        # Validate input
        is_valid, error = self.validate_input(input_path)
        if not is_valid:
            raise ConversionError(error)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = self.get_output_path(input_path)
        
        # Check if output already exists
        if Path(output_path).exists():
            # Add number suffix to avoid overwriting
            base = Path(output_path)
            counter = 1
            while Path(output_path).exists():
                output_path = str(base.parent / f"{base.stem}_{counter}.mp4")
                counter += 1
        
        # Get duration for progress calculation
        duration = self._get_duration(input_path)
        
        self._report_progress(0, "Starting conversion...")
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            '-y',  # Overwrite output
            '-i', input_path,
            '-c:v', 'libx265',
            '-pix_fmt', 'yuv420p10le',
            '-color_primaries', 'bt2020',
            '-colorspace', 'bt2020nc',
            '-color_trc', 'arib-std-b67',
            '-x265-params', 'hdr-opt=1:repeat-headers=1:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:atc-sei=18:pic-struct=0',
            '-tag:v', 'hvc1',
            '-c:a', 'aac',
            '-b:a', '256k',
            '-progress', 'pipe:1',  # Output progress to stdout
            output_path
        ]
        
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            current_time = 0.0
            
            # Read progress from stdout
            for line in self._process.stdout:
                if self._cancelled:
                    raise ConversionError("Conversion cancelled")
                
                line = line.strip()
                
                # Parse progress output
                if line.startswith('out_time='):
                    time_str = line.split('=')[1]
                    if time_str and time_str != 'N/A':
                        current_time = self._parse_time(time_str)
                        if duration and duration > 0:
                            percent = (current_time / duration) * 100
                            self._report_progress(percent, f"Converting... {percent:.1f}%")
                        else:
                            self._report_progress(50, f"Converting... {current_time:.1f}s")
                
                elif line.startswith('progress='):
                    if line == 'progress=end':
                        self._report_progress(100, "Finalizing...")
            
            # Wait for process to complete
            self._process.wait()
            
            if self._cancelled:
                # Clean up partial output
                if Path(output_path).exists():
                    Path(output_path).unlink()
                raise ConversionError("Conversion cancelled")
            
            if self._process.returncode != 0:
                stderr = self._process.stderr.read()
                raise ConversionError(f"FFmpeg error (code {self._process.returncode}):\n{stderr}")
            
            # Verify output exists
            if not Path(output_path).exists():
                raise ConversionError("Conversion failed: output file not created")
            
            self._report_progress(100, "Done!")
            return output_path
            
        except FileNotFoundError:
            raise ConversionError(f"FFmpeg not found at: {self.ffmpeg_path}")
        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(f"Conversion failed: {str(e)}")
        finally:
            self._process = None


def verify_hdr_metadata(file_path: str, ffprobe_path: Optional[str] = None) -> dict:
    """
    Verify HDR metadata in the output file.
    
    Returns a dict with color metadata info.
    """
    if not ffprobe_path:
        ffprobe_path = shutil.which('ffprobe')
    
    if not ffprobe_path:
        return {"error": "ffprobe not available"}
    
    try:
        result = subprocess.run(
            [
                ffprobe_path,
                '-v', 'quiet',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=color_primaries,color_transfer,color_space,pix_fmt',
                '-of', 'json',
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if data.get('streams'):
                stream = data['streams'][0]
                return {
                    "color_primaries": stream.get('color_primaries', 'unknown'),
                    "color_transfer": stream.get('color_transfer', 'unknown'),
                    "color_space": stream.get('color_space', 'unknown'),
                    "pixel_format": stream.get('pix_fmt', 'unknown'),
                    "is_hdr": stream.get('color_transfer') == 'arib-std-b67'
                }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Could not read metadata"}
