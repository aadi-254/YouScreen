@echo off
echo ========================================
echo YouTube Video to PDF Converter Web App
echo ========================================
echo.

echo Checking and installing required packages...
echo.

python -m pip install --upgrade pip --quiet
python -m pip install Flask yt-dlp opencv-python Pillow werkzeug --quiet

echo.
echo Packages installed successfully!
echo.
echo Starting the web server...
echo.
echo The web app will open at: http://127.0.0.1:5000
echo Press CTRL+C to stop the server
echo.

python app.py

echo.
echo Server stopped!
pause
