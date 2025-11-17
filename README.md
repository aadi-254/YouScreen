# 📹 YouScreen - YouTube Video to PDF Converter

A web application that downloads YouTube videos and converts them into PDF documents with frame snapshots.

## ✨ Features

- 🎬 Download any YouTube video
- 📸 Extract frames at custom intervals
- 📄 Generate PDF with captured frames
- 🌐 Clean, modern web interface
- 📱 Mobile responsive design
- ⚡ Real-time processing feedback

## 🚀 Quick Start

### Option 1: Using the Batch File (Windows)
Simply double-click `run.bat` - it will install dependencies and start the server automatically.

### Option 2: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aadi-254/YouScreen.git
   cd YouScreen
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## 📦 Requirements

- Python 3.7+
- Flask
- yt-dlp
- OpenCV
- Pillow

## 🎯 Usage

1. Paste a YouTube video URL
2. Set the frame interval (in seconds)
3. Click "Convert to PDF"
4. Download your generated PDF!

## 📂 Project Structure

```
YouScreen/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── style.css         # Styling
├── downloaded_videos/    # Output folder (auto-created)
├── requirements.txt      # Python dependencies
├── run.bat              # Windows launcher
└── README.md            # Documentation
```

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Video Processing:** yt-dlp, OpenCV
- **Image Processing:** Pillow
- **Frontend:** HTML5, CSS3, JavaScript

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 👨‍💻 Author

[aadi-254](https://github.com/aadi-254)

---

⭐ Star this repo if you find it useful!
