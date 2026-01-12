#!/usr/bin/env python3
"""
HDR Video Converter - Web Interface

A simple web-based interface that opens in your browser.
Uses native file picker for selecting files.
"""

import os
import sys
import json
import threading
import webbrowser
import subprocess
import tempfile
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import socketserver

from converter import HDRConverter, ConversionError, SUPPORTED_EXTENSIONS

# Global state
converter = None
conversion_status = {"status": "idle", "progress": 0, "message": "Ready", "output": None}

PORT = 8765

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDR Video Converter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            max-width: 550px;
            width: 100%;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        h1 { color: #fff; text-align: center; margin-bottom: 8px; font-size: 28px; }
        .subtitle { color: #a0a0a0; text-align: center; margin-bottom: 30px; font-size: 14px; }
        
        .file-input-container {
            border: 2px dashed #0f3460;
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(15, 52, 96, 0.2);
        }
        
        .file-input-container:hover {
            border-color: #1a4f8a;
            background: rgba(26, 79, 138, 0.3);
        }
        
        .file-input-container .icon { font-size: 48px; margin-bottom: 15px; }
        .file-input-container .text { color: #eaeaea; font-size: 16px; margin-bottom: 8px; }
        .file-input-container .hint { color: #a0a0a0; font-size: 12px; }
        
        #fileInput { display: none; }
        #selectedFile { color: #00d26a; margin-top: 15px; font-size: 14px; word-break: break-all; }
        
        .convert-btn {
            display: none;
            width: 100%;
            padding: 16px;
            margin-top: 20px;
            background: linear-gradient(90deg, #00d26a, #00ff88);
            border: none;
            border-radius: 12px;
            color: #000;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .convert-btn:hover { transform: scale(1.02); }
        .convert-btn.show { display: block; }
        
        .progress-container { margin-top: 25px; display: none; }
        .progress-container.show { display: block; }
        
        .progress-bar {
            height: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            overflow: hidden;
        }
        
        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(90deg, #00d26a, #00ff88);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .status { color: #a0a0a0; text-align: center; margin-top: 12px; font-size: 14px; }
        .status.success { color: #00d26a; }
        .status.error { color: #ff6b6b; }
        
        .actions { margin-top: 20px; text-align: center; display: none; }
        .actions.show { display: block; }
        
        .actions button {
            background: #0f3460;
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        
        .actions button:hover { background: #1a4f8a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 HDR Converter</h1>
        <p class="subtitle">Convert videos to HDR/HLG for iPhone</p>
        
        <div class="file-input-container" onclick="document.getElementById('fileInput').click()">
            <div class="icon" id="icon">📁</div>
            <div class="text" id="dropText">Click to select a video file</div>
            <div class="hint">Supports: MP4, MOV, MKV, AVI, WebM</div>
            <div id="selectedFile"></div>
        </div>
        
        <input type="file" id="fileInput" accept=".mp4,.mov,.mkv,.avi,.webm,.m4v,.wmv,.flv">
        
        <button class="convert-btn" id="convertBtn" onclick="startConversion()">
            🚀 Convert to HDR
        </button>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="fill" id="progressFill"></div>
            </div>
            <div class="status" id="status">Converting...</div>
        </div>
        
        <div class="actions" id="actions">
            <button onclick="openOutputFolder()">📂 Open Folder</button>
            <button onclick="reset()">🔄 Convert Another</button>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button onclick="shutdown()" style="background: #333; color: #888; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 12px;">⏹️ Stop Server</button>
        </div>
    </div>
    
    <script>
        let selectedFilePath = null;
        
        const fileInput = document.getElementById('fileInput');
        const selectedFileDiv = document.getElementById('selectedFile');
        const convertBtn = document.getElementById('convertBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const status = document.getElementById('status');
        const actions = document.getElementById('actions');
        const icon = document.getElementById('icon');
        const dropText = document.getElementById('dropText');
        
        let pollInterval = null;
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                selectedFilePath = file.name;
                selectedFileDiv.textContent = '✓ ' + file.name;
                convertBtn.classList.add('show');
                
                // Store the path in session via hidden upload
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/upload', { method: 'POST', body: formData })
                    .then(r => r.json())
                    .then(data => {
                        if (data.path) {
                            selectedFilePath = data.path;
                        }
                    });
            }
        });
        
        function startConversion() {
            if (!selectedFilePath) {
                alert('Please select a file first');
                return;
            }
            
            icon.textContent = '⚙️';
            dropText.textContent = 'Converting...';
            convertBtn.classList.remove('show');
            progressContainer.classList.add('show');
            progressFill.style.width = '0%';
            status.textContent = 'Starting conversion...';
            status.className = 'status';
            actions.classList.remove('show');
            
            fetch('/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: selectedFilePath })
            }).then(r => {
                if (r.ok) startPolling();
            });
        }
        
        function startPolling() {
            pollInterval = setInterval(async () => {
                try {
                    const r = await fetch('/status');
                    const data = await r.json();
                    
                    progressFill.style.width = data.progress + '%';
                    status.textContent = data.message;
                    
                    if (data.status === 'done') {
                        clearInterval(pollInterval);
                        icon.textContent = '✅';
                        dropText.textContent = 'Conversion complete!';
                        status.textContent = 'Saved: ' + data.output.split('/').pop();
                        status.className = 'status success';
                        actions.classList.add('show');
                    } else if (data.status === 'error') {
                        clearInterval(pollInterval);
                        icon.textContent = '❌';
                        dropText.textContent = 'Conversion failed';
                        status.textContent = data.message;
                        status.className = 'status error';
                    }
                } catch (err) {
                    clearInterval(pollInterval);
                }
            }, 500);
        }
        
        function reset() {
            icon.textContent = '📁';
            dropText.textContent = 'Click to select a video file';
            selectedFileDiv.textContent = '';
            progressContainer.classList.remove('show');
            actions.classList.remove('show');
            convertBtn.classList.remove('show');
            fileInput.value = '';
            selectedFilePath = null;
        }
        
        async function openOutputFolder() {
            await fetch('/open-folder');
        }
        
        async function shutdown() {
            if (confirm('Stop the HDR Converter server?')) {
                await fetch('/shutdown');
                document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;color:#fff;font-family:sans-serif;"><div style="text-align:center;"><h2>Server Stopped</h2><p style="color:#888;">You can close this tab.</p></div></div>';
            }
        }
    </script>
</body>
</html>
'''


class HDRHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for the HDR converter."""
    
    uploaded_files = {}  # Store uploaded file paths
    
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        global conversion_status
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(conversion_status).encode())
        
        elif self.path == '/open-folder':
            if conversion_status.get('output'):
                output_path = conversion_status['output']
                if sys.platform == 'darwin':
                    subprocess.run(['open', '-R', output_path])
                elif sys.platform == 'win32':
                    subprocess.run(['explorer', '/select,', output_path])
            self.send_response(200)
            self.end_headers()
        
        elif self.path == '/shutdown':
            self.send_response(200)
            self.end_headers()
            print("\n   Shutdown requested. Goodbye!")
            threading.Thread(target=lambda: os._exit(0), daemon=True).start()
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global converter, conversion_status
        
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                
                if 'multipart/form-data' in content_type:
                    boundary = content_type.split('boundary=')[1].encode()
                    body = self.rfile.read(content_length)
                    parts = body.split(b'--' + boundary)
                    
                    for part in parts:
                        if b'filename="' in part:
                            start = part.find(b'filename="') + 10
                            end = part.find(b'"', start)
                            filename = part[start:end].decode()
                            
                            # Extract file content
                            header_end = part.find(b'\r\n\r\n')
                            if header_end < 0:
                                header_end = part.find(b'\n\n')
                            content_start = header_end + 4 if b'\r\n\r\n' in part else header_end + 2
                            content_end = part.rfind(b'\r\n')
                            if content_end <= content_start:
                                content_end = len(part)
                            
                            file_content = part[content_start:content_end]
                            
                            # Save to temp file
                            temp_dir = Path(tempfile.gettempdir()) / 'hdr_converter'
                            temp_dir.mkdir(exist_ok=True)
                            temp_path = temp_dir / filename
                            
                            with open(temp_path, 'wb') as f:
                                f.write(file_content)
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({'path': str(temp_path)}).encode())
                            return
                
                self.send_response(400)
                self.end_headers()
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        elif self.path == '/convert':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body)
                input_path = data.get('path')
                
                if not input_path or not Path(input_path).exists():
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'File not found'}).encode())
                    return
                
                conversion_status = {
                    "status": "converting",
                    "progress": 0,
                    "message": "Starting...",
                    "output": None
                }
                
                thread = threading.Thread(
                    target=self._convert_file,
                    args=(input_path,),
                    daemon=True
                )
                thread.start()
                
                self.send_response(200)
                self.end_headers()
                
            except Exception as e:
                conversion_status = {
                    "status": "error",
                    "progress": 0,
                    "message": str(e),
                    "output": None
                }
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def _convert_file(self, input_path):
        global converter, conversion_status
        
        def progress_callback(percent, message):
            conversion_status["progress"] = percent
            conversion_status["message"] = message
        
        try:
            converter = HDRConverter(progress_callback=progress_callback)
            output_path = converter.convert(input_path)
            
            conversion_status = {
                "status": "done",
                "progress": 100,
                "message": "Complete!",
                "output": output_path
            }
        except Exception as e:
            conversion_status = {
                "status": "error",
                "progress": 0,
                "message": str(e),
                "output": None
            }


def main():
    """Start the web server and open browser."""
    print("🎬 HDR Video Converter - Web Interface")
    print(f"   Opening browser at http://localhost:{PORT}")
    print("   Press Ctrl+C to stop.\n")
    
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("", PORT), HDRHandler)
    
    # Open browser
    webbrowser.open(f'http://localhost:{PORT}')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n   Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
