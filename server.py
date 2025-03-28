from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import time
import uuid
import subprocess
import json

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "static"
COOKIES_FILE = "cookies.json"  # ✅ JSON format cookies file

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ✅ Home Page Route
@app.route('/')
def home():
    return render_template("index.html")

def delete_old_files():
    """ Purane files delete karega (20 sec se purane) """
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 20:
            os.remove(file_path)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get("url")
    type_ = request.args.get("type", "audio")  # default = audio

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    delete_old_files()

    # ✅ Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}.{ 'mp4' if type_ == 'video' else 'mp3' }"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)

    # ✅ yt-dlp command setup with JSON cookies
    command = [
        "yt-dlp",
        "-f", "bestaudio/best" if type_ == "audio" else "best[ext=mp4]",
        "--extract-audio" if type_ == "audio" else "",
        "--audio-format", "mp3" if type_ == "audio" else "",
        "--output", output_path,
        "--cookies-from-browser", "chrome",  # ✅ JSON format cookies ka use
        url
    ]
    
    # ✅ Remove empty strings from command
    command = [arg for arg in command if arg]

    try:
        subprocess.run(command, check=True)
        return jsonify({
            "file_url": f"https://vikasrajput-api.onrender.com/static/{unique_filename}",
            "message": "Download successful"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
