from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "static"
COOKIES_FILE = "cookies.txt"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Function to delete old files (older than 10 sec)
def delete_old_files():
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 10:
            os.remove(file_path)

@app.route('/download', methods=['GET'])
def download_audio():
    video_url = request.args.get("url")
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    delete_old_files()  # Clean old files

    unique_filename = f"{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)

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
        return jsonify({"file_url": f"http://mirrykal.onrender.com/static/{unique_filename}", "message": "Download successful"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

# YouTube Channel API (Hardcoded)
@app.route('/channel', methods=['GET'])
def get_channel():
    return jsonify({"channel_link": "https://m.youtube.com/mirrykal"})

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
