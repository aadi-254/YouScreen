from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL
import cv2
from PIL import Image
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloaded_videos'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Ensure the download folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    try:
        video_url = request.form.get('video_url')
        frame_interval = request.form.get('frame_interval', '20')
        
        # Check if cookies file was uploaded
        cookies_file = request.files.get('cookies_file')
        cookies_path = None
        
        if cookies_file and cookies_file.filename:
            # Save cookies file temporarily
            request_id = str(uuid.uuid4())[:8]
            cookies_filename = secure_filename(f'{request_id}_cookies.txt')
            cookies_path = os.path.join(app.config['UPLOAD_FOLDER'], cookies_filename)
            cookies_file.save(cookies_path)
        
        # Validate inputs
        if not video_url:
            return jsonify({'error': 'Please provide a video URL'}), 400
        
        if not frame_interval.isdigit() or int(frame_interval) <= 0:
            return jsonify({'error': 'Frame interval must be a positive number'}), 400
        
        frame_interval_seconds = int(frame_interval)
        
        # Generate unique ID for this request
        if not cookies_path:
            request_id = str(uuid.uuid4())[:8]
        
        # Download video with multiple fallback methods
        download_options = {
            'format': 'best',  # Accept any best available format
            'outtmpl': f'{app.config["UPLOAD_FOLDER"]}/{request_id}_%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_creator', 'ios', 'mweb'],
                    'player_skip': ['configs', 'webpage'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.apps.youtube.creator/23.43.101 (Linux; U; Android 13; en_US)',
            },
        }
        
        # Add cookies if provided
        if cookies_path:
            download_options['cookiefile'] = cookies_path
        
        try:
            with YoutubeDL(download_options) as ydl:
                info = ydl.extract_info(video_url, download=True)
                video_title = info['title']
                video_filename = ydl.prepare_filename(info)
                video_path = video_filename
        except Exception as e:
            error_msg = str(e)
            if 'Sign in to confirm' in error_msg or 'bot' in error_msg:
                return jsonify({
                    'error': '⚠️ YouTube bot detection active on this server.',
                    'message': 'This hosting server IP is flagged by YouTube. Alternatives:',
                    'solutions': [
                        '✓ Try videos from: Vimeo, Dailymotion, Facebook, Twitter, Instagram',
                        '✓ Use the desktop app (run.bat) instead - works perfectly!',
                        '✓ Some YouTube videos may still work - try different ones'
                    ]
                }), 403
            return jsonify({'error': f'Download error: {error_msg}'}), 500
        
        # Check if video exists
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video download failed'}), 500
        
        # Extract frames
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            return jsonify({'error': 'Could not open video file'}), 500
        
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        frame_interval_frames = int(fps * frame_interval_seconds)
        
        frames = []
        frame_count = 0
        captured_count = 0
        
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            if frame_count % frame_interval_frames == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
                captured_count += 1
            
            frame_count += 1
        
        video.release()
        
        # Create PDF
        if frames:
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)
            pdf_filename = f"{request_id}_{safe_title}_frames.pdf"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            
            frames[0].save(pdf_path, save_all=True, append_images=frames[1:], resolution=100.0)
            
            # Clean up video file and cookies
            try:
                os.remove(video_path)
                if cookies_path and os.path.exists(cookies_path):
                    os.remove(cookies_path)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': f'PDF created successfully with {captured_count} frames',
                'pdf_filename': pdf_filename,
                'video_title': video_title,
                'frames_captured': captured_count,
                'duration': f"{duration:.1f}"
            })
        else:
            return jsonify({'error': 'No frames were captured'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
