from flask import Flask, request, jsonify, send_from_directory, render_template
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

# ✅ Home Page Route (Yahan HTML render hoga)
@app.route('/')
def home():
    return render_template("index.html")  # Ye `templates/index.html` file serve karega

def delete_old_files():
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

    if type_ == "video":
        unique_filename = f"{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
        command = [
            "yt-dlp",
            "-f", "best[ext=mp4]",
            "--output", output_path,
            "--cookies", COOKIES_FILE,
            url
        ]
    else:
        unique_filename = f"{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", output_path,
            "--cookies", COOKIES_FILE,
            url
        ]

    try:
        subprocess.run(command, check=True)
        return jsonify({
            "file_url": f"https://vikasrajput-api.onrender.com/static/{unique_filename}",
            "message": "Download successful"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
