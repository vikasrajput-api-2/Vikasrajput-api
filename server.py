from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

# Folder structure
AUDIO_FOLDER = "static/audio"
VIDEO_FOLDER = "static/video"
COOKIES_FILE = "cookies.txt"

# Create folders if not exist
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Delete old files (older than 60 seconds)
def delete_old_files(folder):
    now = time.time()
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path) and now - os.path.getctime(file_path) > 60:
            os.remove(file_path)

# AUDIO DOWNLOAD ROUTE
@app.route('/download/audio', methods=['GET'])
def download_audio():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    delete_old_files(AUDIO_FOLDER)

    filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(AUDIO_FOLDER, filename)

    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", output_path,
        "--cookies", COOKIES_FILE,
        video_url
    ]

    try:
        subprocess.run(command, check=True)
        return jsonify({
            "file_url": f"https://vikasrajput-api.onrender.com/static/audio/{filename}",
            "message": "Audio download successful"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

# VIDEO DOWNLOAD ROUTE
@app.route('/download/video', methods=['GET'])
def download_video():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    delete_old_files(VIDEO_FOLDER)

    filename = f"{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(VIDEO_FOLDER, filename)

    command = [
        "yt-dlp",
        "-f", "22",  # 720p video+audio combined format (adjust if needed)
        "--output", output_path,
        "--cookies", COOKIES_FILE,
        video_url
    ]

    try:
        subprocess.run(command, check=True)
        return jsonify({
            "file_url": f"https://vikasrajput-api.onrender.com/static/video/{filename}",
            "message": "Video download successful"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

# STATIC FILE SERVING ROUTES
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/static/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

# YOUTUBE CHANNEL ROUTE
@app.route('/channel', methods=['GET'])
def get_channel():
    return jsonify({"channel_link": "https://m.youtube.com/mirrykal"})

# DISABLE CACHE
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

# SERVER START
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
        
