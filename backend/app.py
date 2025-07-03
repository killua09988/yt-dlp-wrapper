#!/usr/bin/env python3
"""
YouTube Video Downloader Flask Backend
Created with Comet Assistant

This Flask application provides a REST API for downloading YouTube videos using yt-dlp.
It accepts POST requests to /download with a YouTube URL and processes the download.
"""

import os
import json
import uuid
import logging
import tempfile
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
CONFIG = {
    'DOWNLOAD_DIR': os.path.join(tempfile.gettempdir(), 'yt_downloads'),
    'MAX_FILE_SIZE': 500 * 1024 * 1024,  # 500MB limit
    'ALLOWED_FORMATS': ['mp4', 'webm', 'mkv'],
    'DEFAULT_QUALITY': 'best[height<=720]',  # Default to 720p max
}

# Ensure download directory exists
os.makedirs(CONFIG['DOWNLOAD_DIR'], exist_ok=True)

# YouTube URL validation regex (same as frontend)
YOUTUBE_REGEX_PATTERNS = [
    r'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
    r'^https?://(www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    r'^https?://(www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    r'^https?://(www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
]

def is_valid_youtube_url(url):
    """Validate if the URL is a valid YouTube URL."""
    import re
    if not url or not isinstance(url, str):
        return False
    
    return any(re.match(pattern, url.strip()) for pattern in YOUTUBE_REGEX_PATTERNS)

def get_video_info(url):
    """Extract basic video information without downloading."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return None

def download_video(url, output_path):
    """Download video using yt-dlp."""
    # Generate unique filename
    download_id = str(uuid.uuid4())[:8]
    
    ydl_opts = {
        'format': CONFIG['DEFAULT_QUALITY'],
        'outtmpl': os.path.join(output_path, f'{download_id}_%(title)s.%(ext)s'),
        'restrictfilenames': True,  # Avoid special characters in filenames
        'noplaylist': True,  # Only download single video, not playlist
        'extractaudio': False,
        'writeinfojson': False,
        'writethumbnail': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info first to get the final filename
            info = ydl.extract_info(url, download=False)
            
            # Check file size estimate
            filesize = info.get('filesize') or info.get('filesize_approx', 0)
            if filesize > CONFIG['MAX_FILE_SIZE']:
                raise ValueError(f"File too large: {filesize / (1024*1024):.1f}MB > {CONFIG['MAX_FILE_SIZE'] / (1024*1024):.1f}MB")
            
            # Download the video
            ydl.download([url])
            
            # Find the downloaded file
            expected_filename = ydl.prepare_filename(info)
            
            # The actual filename might be different due to restrictfilenames
            download_dir = Path(output_path)
            downloaded_files = list(download_dir.glob(f'{download_id}_*'))
            
            if downloaded_files:
                downloaded_file = downloaded_files[0]
                return {
                    'success': True,
                    'filename': downloaded_file.name,
                    'filepath': str(downloaded_file),
                    'title': info.get('title', 'Unknown'),
                    'size': downloaded_file.stat().st_size if downloaded_file.exists() else 0
                }
            else:
                raise FileNotFoundError("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise

@app.route('/')
def index():
    """Serve the frontend HTML."""
    # This is a simple way to serve the frontend files
    # In production, you'd typically use a web server like nginx
    frontend_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Downloader</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { text-align: center; }
            .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouTube Downloader API</h1>
            <div class="info">
                <h3>API Endpoints:</h3>
                <p><strong>POST /download</strong> - Download a YouTube video</p>
                <p><strong>GET /health</strong> - Check API health</p>
                <br>
                <p>Frontend files should be served separately.</p>
                <p>Send POST requests to /download with JSON: {"url": "https://youtube.com/watch?v=..."}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return frontend_html

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/download', methods=['POST'])
def download_youtube_video():
    """Handle video download requests."""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        # Validate YouTube URL
        if not is_valid_youtube_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL'
            }), 400
        
        logger.info(f"Processing download request for: {url}")
        
        # Get video info first
        video_info = get_video_info(url)
        if not video_info:
            return jsonify({
                'success': False,
                'error': 'Could not extract video information'
            }), 400
        
        # Download the video
        try:
            download_result = download_video(url, CONFIG['DOWNLOAD_DIR'])
            
            if download_result['success']:
                # For this example, we'll return success without actual file serving
                # In production, you might want to:
                # 1. Store files temporarily and provide download links
                # 2. Stream files directly
                # 3. Use cloud storage
                
                response_data = {
                    'success': True,
                    'message': 'Video downloaded successfully',
                    'video_info': video_info,
                    'filename': download_result['filename'],
                    'size': download_result['size'],
                    # 'download_url': f'/files/{download_result["filename"]}',  # For file serving
                }
                
                logger.info(f"Successfully downloaded: {download_result['filename']}")
                return jsonify(response_data)
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Download failed: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    """Serve downloaded files (optional endpoint for file delivery)."""
    try:
        file_path = os.path.join(CONFIG['DOWNLOAD_DIR'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Security check - ensure file is in download directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(CONFIG['DOWNLOAD_DIR'])):
            return jsonify({'error': 'Access denied'}), 403
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"File serving error: {str(e)}")
        return jsonify({'error': 'File serving failed'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Set to False in production
    )

# created with Comet Assistant
