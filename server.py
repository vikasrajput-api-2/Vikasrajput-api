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
COOKIES_JSON = "cookies.json"  # JSON cookies file
COOKIES_TXT = "cookies.txt"    # Netscape format cookies file

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template("index.html")

def convert_cookies():
    """ Convert JSON Cookies to Netscape format """
    try:
        with open(COOKIES_JSON, "r", encoding="utf-8") as file:
            cookies = json.load(file)

        netscape_cookies = ""
        for cookie in cookies:
            netscape_cookies += f"{cookie['domain']}   TRUE   {cookie['path']}   {'TRUE' if cookie['secure'] else 'FALSE'}   {cookie.get('expiry', '0')}   {cookie['name']}   {cookie['value']}\n"

        with open(COOKIES_TXT, "w", encoding="utf-8") as file:
            file.write(netscape_cookies)

        print("✅ Cookies converted to Netscape format (cookies.txt)")
    except Exception as e:
        print(f"❌ Error converting cookies: {str(e)}")

def delete_old_files():
    """ Delete old files (older than 5 minutes) """
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 300:
            os.remove(file_path)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get("url")
    type_ = request.args.get("type", "audio")  # Default: audio

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    convert_cookies()  # Convert cookies first

    # Generate unique filename
    file_ext = "mp3" if type_ == "audio" else "mp4"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
    
    # Fix yt-dlp command
    if type_ == "audio":
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "--cookies", COOKIES_TXT,
            url
        ]
    elif type_ == "video":
        command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
            "--merge-output-format", "mp4",
            "--output", os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "--cookies", COOKIES_TXT,
            url
        ]
    else:
        return jsonify({"error": "Invalid type. Use 'audio' or 'video'."}), 400

    try:
        subprocess.run(command, check=True)
        delete_old_files()  # Delete old files AFTER download
        
        # Find downloaded file
        downloaded_file = None
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.endswith(file_ext):
                downloaded_file = file
                break

        if not downloaded_file:
            return jsonify({"error": "Download failed: File not found"}), 500

        return jsonify({
            "file_url": f"https://vikasrajput-api.onrender.com/static/{downloaded_file}",
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
                                                                                  
