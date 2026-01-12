#!/usr/bin/env python3
"""
HDR Video Converter - Web Interface

A simple web-based interface for converting videos to HDR/HLG format.
Opens in your default browser.
"""

import os
import sys
import json
import threading
import webbrowser
import subprocess
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import socketserver

from converter import HDRConverter, ConversionError, SUPPORTED_EXTENSIONS

# Global state
converter = None
conversion_status = {"status": "idle", "progress": 0, "message": "Ready", "output": None}
output_folder = None

PORT = 8765

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDR Video Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
            max-width: 500px;
            width: 100%;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 8px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #a0a0a0;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .drop-zone {
            border: 2px dashed #0f3460;
            border-radius: 16px;
            padding: 50px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(15, 52, 96, 0.2);
        }
        
        .drop-zone:hover, .drop-zone.drag-over {
            border-color: #1a4f8a;
            background: rgba(26, 79, 138, 0.3);
        }
        
        .drop-zone .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .drop-zone .text {
            color: #eaeaea;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .drop-zone .hint {
            color: #a0a0a0;
            font-size: 12px;
        }
        
        .output-selector {
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #a0a0a0;
            font-size: 13px;
        }
        
        .output-selector button {
            background: #0f3460;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .output-selector button:hover {
            background: #1a4f8a;
        }
        
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        
        .progress-container.show {
            display: block;
        }
        
        .progress-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(90deg, #00d26a, #00ff88);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .status {
            color: #a0a0a0;
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
        }
        
        .status.success {
            color: #00d26a;
        }
        
        .status.error {
            color: #ff6b6b;
        }
        
        .actions {
            margin-top: 20px;
            text-align: center;
            display: none;
        }
        
        .actions.show {
            display: block;
        }
        
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
        
        .actions button:hover {
            background: #1a4f8a;
        }
        
        input[type="file"] {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 HDR Converter</h1>
        <p class="subtitle">Convert videos to HDR/HLG for iPhone</p>
        
        <div class="drop-zone" id="dropZone">
            <div class="icon" id="icon">📁</div>
            <div class="text" id="dropText">Drop a video here or click to browse</div>
            <div class="hint">Supports: MP4, MOV, MKV, AVI, WebM</div>
        </div>
        
        <input type="file" id="fileInput" accept=".mp4,.mov,.mkv,.avi,.webm,.m4v,.wmv,.flv">
        
        <div class="output-selector">
            <span id="outputPath">📂 Output: Same as input</span>
            <button onclick="selectOutputFolder()">Change</button>
        </div>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="fill" id="progressFill"></div>
            </div>
            <div class="status" id="status">Converting...</div>
        </div>
        
        <div class="actions" id="actions">
            <button onclick="openOutputFolder()">📂 Open Folder</button>
            <button onclick="reset()">Convert Another</button>
        </div>
    </div>
    
    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const icon = document.getElementById('icon');
        const dropText = document.getElementById('dropText');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const status = document.getElementById('status');
        const actions = document.getElementById('actions');
        
        let pollInterval = null;
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        });
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) handleFile(file);
        });
        
        async function handleFile(file) {
            icon.textContent = '⚙️';
            dropText.textContent = 'Converting: ' + file.name;
            progressContainer.classList.add('show');
            progressFill.style.width = '0%';
            status.textContent = 'Starting conversion...';
            status.className = 'status';
            actions.classList.remove('show');
            
            // Send file path for conversion
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    startPolling();
                } else {
                    showError('Failed to start conversion');
                }
            } catch (err) {
                showError('Error: ' + err.message);
            }
        }
        
        function startPolling() {
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    
                    progressFill.style.width = data.progress + '%';
                    status.textContent = data.message;
                    
                    if (data.status === 'done') {
                        clearInterval(pollInterval);
                        showSuccess(data.output);
                    } else if (data.status === 'error') {
                        clearInterval(pollInterval);
                        showError(data.message);
                    }
                } catch (err) {
                    clearInterval(pollInterval);
                    showError('Connection lost');
                }
            }, 500);
        }
        
        function showSuccess(output) {
            icon.textContent = '✅';
            dropText.textContent = 'Conversion complete!';
            status.textContent = 'Saved: ' + output;
            status.className = 'status success';
            actions.classList.add('show');
        }
        
        function showError(message) {
            icon.textContent = '❌';
            dropText.textContent = 'Conversion failed';
            status.textContent = message;
            status.className = 'status error';
            progressContainer.classList.remove('show');
        }
        
        function reset() {
            icon.textContent = '📁';
            dropText.textContent = 'Drop a video here or click to browse';
            progressContainer.classList.remove('show');
            actions.classList.remove('show');
            fileInput.value = '';
        }
        
        async function selectOutputFolder() {
            alert('Output folder selection requires native file picker.\\nFiles will be saved next to the input file.');
        }
        
        async function openOutputFolder() {
            await fetch('/open-folder');
        }
    </script>
</body>
</html>
'''


class HDRHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for the HDR converter."""
    
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
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global converter, conversion_status
        
        if self.path == '/convert':
            try:
                # Parse multipart form data to get filename
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                
                if 'multipart/form-data' in content_type:
                    # Read boundary
                    boundary = content_type.split('boundary=')[1].encode()
                    body = self.rfile.read(content_length)
                    
                    # Parse filename from Content-Disposition
                    parts = body.split(b'--' + boundary)
                    for part in parts:
                        if b'filename="' in part:
                            start = part.find(b'filename="') + 10
                            end = part.find(b'"', start)
                            filename = part[start:end].decode()
                            
                            # Save uploaded file temporarily
                            temp_dir = Path.home() / 'Downloads'
                            input_path = str(temp_dir / filename)
                            
                            # Extract file content
                            content_start = part.find(b'\\r\\n\\r\\n') + 4
                            if content_start < 4:
                                content_start = part.find(b'\\n\\n') + 2
                            content_end = part.rfind(b'\\r\\n')
                            if content_end < 0:
                                content_end = len(part)
                            
                            file_content = part[content_start:content_end]
                            
                            with open(input_path, 'wb') as f:
                                f.write(file_content)
                            
                            # Start conversion
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
                            return
                
                self.send_response(400)
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
    print("Starting HDR Converter...")
    print(f"Opening browser at http://localhost:{PORT}")
    
    # Start server in background
    with socketserver.TCPServer(("", PORT), HDRHandler) as httpd:
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}')
        
        print("Server running. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == '__main__':
    main()
