from yt_dlp import YoutubeDL
import cv2
from PIL import Image
import os

print("---- welcome to the YouTube Video Downloader & PDF Creator ----\n")
# Specify the URL of the YouTube video you want to download
video_url = input("enter your video link : ")
frames_input = input("enter the frame interval in seconds: ")
if(not frames_input.isdigit() or int(frames_input) <= 0):
    print("Invalid input for frame interval. Please enter a positive integer.")
    exit(1)

# Specify download options
download_options = {
    'format': 'best[ext=mp4]/best',  # Download best single file (no merging needed)
    'outtmpl': 'downloaded_videos/%(title)s.%(ext)s',  # Output template for downloaded files
    'quiet': False,  # Set to True if you don't want console output
}

# Create a YoutubeDL instance with the specified options
print("\n[1/3] Downloading video...")
with YoutubeDL(download_options) as ydl:
    # Download the video
    info = ydl.extract_info(video_url, download=True)
    video_title = info['title']
    video_ext = info['ext']
    # Get the actual filename from yt-dlp
    video_filename = ydl.prepare_filename(info)
    video_path = video_filename

print('Video downloaded successfully!')
print(f"Video saved as: {video_path}")

# Extract frames every 5 seconds
print("\n[2/3] Extracting frames every 20 seconds...")
print(f"Opening video file: {video_path}")

# Check if file exists
if not os.path.exists(video_path):
    print(f"Error: Video file not found at {video_path}")
    exit(1)

video = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not video.isOpened():
    print("Error: Could not open video file. Trying alternative path...")
    # Sometimes the extension might be different, try to find the actual file
    video_dir = "downloaded_videos"
    files = [f for f in os.listdir(video_dir) if video_title in f]
    if files:
        video_path = os.path.join(video_dir, files[0])
        print(f"Found video at: {video_path}")
        video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print("Error: Still could not open video. Please check the file format.")
        exit(1)

fps = video.get(cv2.CAP_PROP_FPS)
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps > 0 else 0

print(f"Video info: {fps:.2f} FPS, {total_frames} frames, {duration:.1f} seconds")

#frame per second interval
frame_interval = int(fps * int(frames_input))  # Capture every specified seconds

frames = []
frame_count = 0
captured_count = 0

while True:
    ret, frame = video.read()
    if not ret:
        break
    
    if frame_count % frame_interval == 0:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(frame_rgb))
        captured_count += 1
        print(f"  Captured frame {captured_count} at {frame_count/fps:.1f} seconds")
    
    frame_count += 1

video.release()
print(f"Total frames captured: {captured_count}")

# Create PDF from frames
if frames:
    print("\n[3/3] Creating PDF...")
    # Use a safe filename for the PDF
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)
    pdf_path = f"downloaded_videos/{safe_title}_frames.pdf"
    frames[0].save(pdf_path, save_all=True, append_images=frames[1:], resolution=100.0)
    print(f"\nPDF created successfully: {pdf_path}")
else:
    print("No frames were captured!")
