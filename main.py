#!/usr/bin/env python3
"""
HDR Video Converter - Main Application

A simple desktop application that converts standard video files to HDR format (HLG)
for iPhone compatibility. Features drag-and-drop interface with progress tracking.
"""

import os
import sys
import threading
import subprocess
from pathlib import Path
from typing import Optional

# Check for tkinter availability
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("Error: tkinter is required. Please install it:")
    print("  macOS: Should be included with Python")
    print("  Linux: sudo apt-get install python3-tk")
    sys.exit(1)

# Try to import drag-and-drop support (may crash on some macOS versions)
HAS_DND = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception as e:
    # tkinterdnd2 not available or incompatible with this macOS version
    # App will work with file browser instead of drag-and-drop
    pass

from converter import HDRConverter, ConversionError, SUPPORTED_EXTENSIONS


class HDRConverterApp:
    """Main application window for HDR video conversion."""
    
    # Color scheme (dark theme)
    COLORS = {
        'bg': '#1a1a2e',
        'bg_secondary': '#16213e',
        'accent': '#0f3460',
        'accent_hover': '#1a4f8a',
        'success': '#00d26a',
        'error': '#ff6b6b',
        'text': '#eaeaea',
        'text_secondary': '#a0a0a0',
        'border': '#0f3460',
        'drop_zone': '#16213e',
        'drop_zone_active': '#1a4f8a',
    }
    
    def __init__(self):
        """Initialize the application."""
        # Create main window (with drag-drop if available)
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        
        self.root.title("HDR Converter")
        self.root.geometry("500x450")
        self.root.minsize(400, 400)
        self.root.configure(bg=self.COLORS['bg'])
        
        # State
        self.converter: Optional[HDRConverter] = None
        self.is_converting = False
        self.current_file: Optional[str] = None
        self.output_file: Optional[str] = None
        self.output_folder: Optional[str] = None  # Custom output folder
        
        # Setup UI
        self._setup_styles()
        self._create_menu()
        self._create_widgets()
        self._setup_drag_drop()
        
        # Center window
        self._center_window()
        
        # Check for updates
        self._start_update_check()
    
    def _start_update_check(self):
        """Start background update check."""
        thread = threading.Thread(target=self._check_for_updates, daemon=True)
        thread.start()
    
    def _check_for_updates(self):
        """Check GitHub for new releases."""
        try:
            import requests
            response = requests.get(
                "https://api.github.com/repos/AndrewStrupinski/HDR-Video-Converter/releases/latest",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                latest_tag = data['tag_name']
                latest_version = latest_tag.lstrip('v')
                current_version = os.environ.get('APP_VERSION', 'Development').lstrip('v')
                
                # Check if newer (simple string comparison works for v1.0.X)
                # Ideally semver, but this is sufficient for now
                if current_version != 'Development' and latest_version > current_version:
                    self.root.after(0, lambda: self._show_update_banner(latest_tag, data['html_url']))
                    
        except Exception:
            # Silently fail on network errors
            pass
            
    def _show_update_banner(self, version: str, url: str):
        """Show update available banner."""
        import webbrowser
        
        banner = tk.Frame(self.main_frame, bg='#2ecc71', cursor='hand2')
        banner.pack(fill=tk.X, before=self.drop_frame, pady=(0, 10))
        
        label = tk.Label(
            banner,
            text=f"✨ New version {version} available! Click to download.",
            font=('SF Pro Text', 11, 'bold'),
            bg='#2ecc71',
            fg='white'
        )
        label.pack(pady=5)
        
        # Make clickable
        for widget in [banner, label]:
            widget.bind('<Button-1>', lambda e: webbrowser.open(url))
    
    def _create_menu(self):
        """Create the application menu bar."""
        import webbrowser
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="GitHub Repository", command=lambda: webbrowser.open("https://github.com/AndrewStrupinski/HDR-Video-Converter"))
        help_menu.add_separator()
        help_menu.add_command(label="About HDR Converter", command=self._show_about)
    
    def _show_about(self):
        """Show the About dialog."""
        import webbrowser
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About HDR Converter")
        about_window.geometry("400x280")
        about_window.resizable(False, False)
        about_window.configure(bg=self.COLORS['bg'])
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center on parent
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 140
        about_window.geometry(f"+{x}+{y}")
        
        # App icon
        tk.Label(about_window, text="🎬", font=('', 48), bg=self.COLORS['bg']).pack(pady=(20, 10))
        
        # App name
        tk.Label(about_window, text="HDR Video Converter", font=('SF Pro Display', 18, 'bold'),
                 bg=self.COLORS['bg'], fg=self.COLORS['text']).pack()
        
        # Version
        version = os.environ.get('APP_VERSION', 'Development').lstrip('v')
        tk.Label(about_window, text=f"Version {version}", font=('SF Pro Text', 12),
                 bg=self.COLORS['bg'], fg=self.COLORS['text_secondary']).pack(pady=(5, 10))
        
        # Description
        tk.Label(about_window, text="Convert videos to HDR/HLG format for iPhone",
                 font=('SF Pro Text', 11), bg=self.COLORS['bg'], fg=self.COLORS['text']).pack()
        
        # Copyright
        tk.Label(about_window, text="© 2026 Andrew Strupinski. MIT License.",
                 font=('SF Pro Text', 10), bg=self.COLORS['bg'], fg=self.COLORS['text_secondary']).pack(pady=(10, 5))
        
        # GitHub link
        github_label = tk.Label(about_window, text="GitHub Repository", font=('SF Pro Text', 11, 'underline'),
                               bg=self.COLORS['bg'], fg='#4da6ff', cursor='hand2')
        github_label.pack(pady=5)
        github_label.bind('<Button-1>', lambda e: webbrowser.open("https://github.com/AndrewStrupinski/HDR-Video-Converter"))
        
        # Close button - focus=0 removes the weird selection line
        close_btn = tk.Button(about_window, text="Close", command=about_window.destroy,
                 bg=self.COLORS['accent'], fg=self.COLORS['text'], relief=tk.FLAT,
                 activebackground=self.COLORS['accent_hover'], activeforeground=self.COLORS['text'],
                 padx=20, pady=5, highlightthickness=0, bd=0)
        close_btn.pack(pady=15)
        
        # Remove focus from button on Mac to avoid blue ring
        close_btn.bind('<FocusIn>', lambda e: about_window.focus_set())
    
    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Progress bar style
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.COLORS['bg_secondary'],
            background=self.COLORS['success'],
            bordercolor=self.COLORS['border'],
            lightcolor=self.COLORS['success'],
            darkcolor=self.COLORS['success'],
        )
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="HDR Video Converter",
            font=('SF Pro Display', 24, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            self.main_frame,
            text="Convert videos to HDR/HLG for iPhone",
            font=('SF Pro Text', 12),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Drop zone frame
        self.drop_frame = tk.Frame(
            self.main_frame,
            bg=self.COLORS['drop_zone'],
            highlightbackground=self.COLORS['border'],
            highlightthickness=2,
            cursor='hand2'
        )
        self.drop_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Drop zone content
        self.drop_icon = tk.Label(
            self.drop_frame,
            text="📁",
            font=('', 48),
            bg=self.COLORS['drop_zone'],
            fg=self.COLORS['text']
        )
        self.drop_icon.pack(pady=(30, 10))
        
        self.status_label = tk.Label(
            self.drop_frame,
            text="Drop a video here or click to browse",
            font=('SF Pro Text', 14),
            bg=self.COLORS['drop_zone'],
            fg=self.COLORS['text']
        )
        self.status_label.pack(pady=5)
        
        # Supported formats hint
        formats_text = "Supported: " + ", ".join(sorted(ext.upper()[1:] for ext in SUPPORTED_EXTENSIONS))
        self.formats_label = tk.Label(
            self.drop_frame,
            text=formats_text,
            font=('SF Pro Text', 10),
            bg=self.COLORS['drop_zone'],
            fg=self.COLORS['text_secondary']
        )
        self.formats_label.pack(pady=(5, 20))
        
        # Make drop zone clickable
        for widget in [self.drop_frame, self.drop_icon, self.status_label, self.formats_label]:
            widget.bind('<Button-1>', self._browse_file)
        
        # Output folder selector
        self.output_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg'])
        self.output_frame.pack(fill=tk.X, pady=(5, 10))
        
        # Show correct default folder based on platform
        if sys.platform == 'win32':
            default_output = "~/Videos/HDR Converted"
        else:
            default_output = "~/Movies/HDR Converted"
        
        self.output_label = tk.Label(
            self.output_frame,
            text=f"📂 Output: {default_output}",
            font=('SF Pro Text', 11),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_secondary'],
            cursor='hand2'
        )
        self.output_label.pack(side=tk.LEFT)
        self.output_label.bind('<Button-1>', self._select_output_folder)
        
        self.output_change_btn = tk.Button(
            self.output_frame,
            text="Change",
            font=('SF Pro Text', 10),
            bg=self.COLORS['accent'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['accent_hover'],
            activeforeground=self.COLORS['text'],
            relief=tk.FLAT,
            cursor='hand2',
            padx=8,
            pady=2,
            command=self._select_output_folder
        )
        self.output_change_btn.pack(side=tk.RIGHT)
        
        # Progress bar (hidden initially)
        self.progress_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg'])
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            style="Custom.Horizontal.TProgressbar",
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X)
        self.progress_frame.pack_forget()  # Hide initially
        
        # Button frame
        self.button_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg'])
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Open folder button (hidden initially)
        self.open_folder_btn = tk.Button(
            self.button_frame,
            text="📂 Open Output Folder",
            font=('SF Pro Text', 12),
            bg=self.COLORS['accent'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['accent_hover'],
            activeforeground=self.COLORS['text'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._open_output_folder
        )
        
        # Cancel button (hidden initially)
        self.cancel_btn = tk.Button(
            self.button_frame,
            text="Cancel",
            font=('SF Pro Text', 12),
            bg=self.COLORS['error'],
            fg=self.COLORS['text'],
            activebackground='#ff5252',
            activeforeground=self.COLORS['text'],
            relief=tk.FLAT,
            cursor='hand2',
            command=self._cancel_conversion
        )
    
    def _setup_drag_drop(self):
        """Setup drag and drop handling."""
        if not HAS_DND:
            return
        
        # Register drop target
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
        self.drop_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.drop_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
    
    def _on_drag_enter(self, event):
        """Handle drag enter event."""
        if not self.is_converting:
            self.drop_frame.configure(bg=self.COLORS['drop_zone_active'])
            for widget in [self.drop_icon, self.status_label, self.formats_label]:
                widget.configure(bg=self.COLORS['drop_zone_active'])
    
    def _on_drag_leave(self, event):
        """Handle drag leave event."""
        self.drop_frame.configure(bg=self.COLORS['drop_zone'])
        for widget in [self.drop_icon, self.status_label, self.formats_label]:
            widget.configure(bg=self.COLORS['drop_zone'])
    
    def _on_drop(self, event):
        """Handle file drop event."""
        self._on_drag_leave(event)  # Reset appearance
        
        if self.is_converting:
            return
        
        # Parse dropped file path
        file_path = event.data
        
        # Handle multiple files (take first)
        if file_path.startswith('{'):
            # Tkinter wraps paths with spaces in braces
            file_path = file_path.strip('{}')
        elif ' ' in file_path and not os.path.exists(file_path):
            # Multiple files separated by space - take first
            file_path = file_path.split()[0]
        
        self._process_file(file_path)
    
    def _browse_file(self, event=None):
        """Open file browser dialog."""
        if self.is_converting:
            return
        
        filetypes = [
            ('Video files', ' '.join(f'*{ext}' for ext in SUPPORTED_EXTENSIONS)),
            ('All files', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=filetypes
        )
        
        if file_path:
            self._process_file(file_path)
    
    def _select_output_folder(self, event=None):
        """Open folder browser for output location."""
        if self.is_converting:
            return
        
        folder = filedialog.askdirectory(
            title="Select output folder",
            initialdir=self.output_folder or str(Path.home())
        )
        
        if folder:
            self.output_folder = folder
            # Truncate display if too long
            display = folder if len(folder) < 35 else "..." + folder[-32:]
            self.output_label.configure(text=f"📂 Output: {display}")
        else:
            # Reset to default
            self.output_folder = None
            self.output_label.configure(text="📂 Output: Same as input")
    
    def _process_file(self, file_path: str):
        """Start processing the selected file."""
        self.current_file = file_path
        
        # Create converter with progress callback
        def progress_callback(percent: float, message: str):
            self.root.after(0, lambda: self._update_progress(percent, message))
        
        self.converter = HDRConverter(progress_callback=progress_callback)
        
        # Validate file
        is_valid, error = self.converter.validate_input(file_path)
        if not is_valid:
            messagebox.showerror("Invalid File", error)
            return
        
        # Start conversion in background thread
        self.is_converting = True
        self._show_converting_state()
        
        thread = threading.Thread(target=self._convert_thread, daemon=True)
        thread.start()
    
    def _convert_thread(self):
        """Background thread for conversion."""
        try:
            # Determine output path
            if self.output_folder:
                input_path = Path(self.current_file)
                output_path = str(Path(self.output_folder) / f"{input_path.stem}_HDR.mp4")
            else:
                output_path = None  # Use default (same folder as input)
            
            self.output_file = self.converter.convert(self.current_file, output_path)
            self.root.after(0, self._show_success_state)
        except ConversionError as e:
            self.root.after(0, lambda: self._show_error_state(str(e)))
        except Exception as e:
            self.root.after(0, lambda: self._show_error_state(f"Unexpected error: {str(e)}"))
        finally:
            self.is_converting = False
    
    def _update_progress(self, percent: float, message: str):
        """Update progress bar and status."""
        self.progress_bar['value'] = percent
        self.status_label.configure(text=message)
    
    def _show_converting_state(self):
        """Update UI to show conversion in progress."""
        filename = Path(self.current_file).name
        self.drop_icon.configure(text="⚙️")
        self.status_label.configure(text=f"Converting: {filename}", fg=self.COLORS['text'])
        self.formats_label.configure(text="This may take a while for large files...")
        
        # Show progress bar
        self.progress_bar['value'] = 0
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        # Show cancel button
        self.open_folder_btn.pack_forget()
        self.cancel_btn.pack(pady=5)
        
        # Disable drop zone
        for widget in [self.drop_frame, self.drop_icon, self.status_label, self.formats_label]:
            widget.configure(cursor='wait')
    
    def _show_success_state(self):
        """Update UI to show successful conversion."""
        self.drop_icon.configure(text="✅")
        self.status_label.configure(text="Conversion complete!", fg=self.COLORS['success'])
        
        output_name = Path(self.output_file).name
        self.formats_label.configure(text=f"Saved as: {output_name}")
        
        # Hide progress and cancel button
        self.progress_frame.pack_forget()
        self.cancel_btn.pack_forget()
        
        # Show open folder button
        self.open_folder_btn.pack(pady=5)
        
        # Re-enable drop zone
        for widget in [self.drop_frame, self.drop_icon, self.status_label, self.formats_label]:
            widget.configure(cursor='hand2')
        
        # Reset after 10 seconds
        self.root.after(10000, self._reset_ui)
    
    def _show_error_state(self, error_message: str):
        """Update UI to show error."""
        self.drop_icon.configure(text="❌")
        self.status_label.configure(text="Conversion failed", fg=self.COLORS['error'])
        
        # Truncate long error messages
        if len(error_message) > 100:
            display_error = error_message[:100] + "..."
        else:
            display_error = error_message
        self.formats_label.configure(text=display_error)
        
        # Hide progress and cancel button
        self.progress_frame.pack_forget()
        self.cancel_btn.pack_forget()
        
        # Re-enable drop zone
        for widget in [self.drop_frame, self.drop_icon, self.status_label, self.formats_label]:
            widget.configure(cursor='hand2')
        
        # Show full error in dialog
        messagebox.showerror("Conversion Error", error_message)
        
        # Reset after 5 seconds
        self.root.after(5000, self._reset_ui)
    
    def _reset_ui(self):
        """Reset UI to initial state."""
        if self.is_converting:
            return
        
        self.drop_icon.configure(text="📁")
        self.status_label.configure(
            text="Drop a video here or click to browse",
            fg=self.COLORS['text']
        )
        formats_text = "Supported: " + ", ".join(sorted(ext.upper()[1:] for ext in SUPPORTED_EXTENSIONS))
        self.formats_label.configure(text=formats_text)
        
        self.open_folder_btn.pack_forget()
        self.progress_frame.pack_forget()
    
    def _cancel_conversion(self):
        """Cancel the current conversion."""
        if self.converter and self.is_converting:
            self.converter.cancel()
            self.status_label.configure(text="Cancelling...", fg=self.COLORS['text_secondary'])
    
    def _open_output_folder(self):
        """Open the folder containing the output file."""
        if self.output_file and Path(self.output_file).exists():
            folder = Path(self.output_file).parent
            
            if sys.platform == 'darwin':
                # macOS: reveal in Finder
                subprocess.run(['open', '-R', self.output_file])
            elif sys.platform == 'win32':
                # Windows: open Explorer and select file
                subprocess.run(['explorer', '/select,', self.output_file])
            else:
                # Linux: just open folder
                subprocess.run(['xdg-open', str(folder)])
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = HDRConverterApp()
    app.run()


if __name__ == '__main__':
    main()
