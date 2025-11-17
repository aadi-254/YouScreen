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
        
        # Validate inputs
        if not video_url:
            return jsonify({'error': 'Please provide a video URL'}), 400
        
        if not frame_interval.isdigit() or int(frame_interval) <= 0:
            return jsonify({'error': 'Frame interval must be a positive number'}), 400
        
        frame_interval_seconds = int(frame_interval)
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]
        
        # Download video with bot detection workarounds
        download_options = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'{app.config["UPLOAD_FOLDER"]}/{request_id}_%(title)s.%(ext)s',
            'quiet': True,
            'nocheckcertificate': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'cookiefile': None,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        with YoutubeDL(download_options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info['title']
            video_filename = ydl.prepare_filename(info)
            video_path = video_filename
        
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
            
            # Clean up video file
            try:
                os.remove(video_path)
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
