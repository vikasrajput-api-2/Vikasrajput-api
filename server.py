from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import time
import uuid
import subprocess
import json

app = Flask(__name__, template_folder="templates")
CORS(app)

DOWNLOAD_FOLDER = "static"
COOKIES_JSON = "cookies.json"  # JSON cookies file
COOKIES_TXT = "cookies.txt"    # Netscape format cookies file

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ✅ Function to convert JSON cookies to Netscape format
def convert_cookies():
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

# ✅ Function to delete old files (older than 10 sec)
def delete_old_files():
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 10:
            os.remove(file_path)

@app.route('/')
def home():
    return render_template("index.html")  # Show HTML page on homepage

@app.route('/download', methods=['GET'])
def download_media():
    video_url = request.args.get("url")
    media_type = request.args.get("type", "audio")  # Default: Audio

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    delete_old_files()  # Clean old files
    convert_cookies()   # ✅ Convert cookies before downloading

    unique_filename = f"{uuid.uuid4().hex}.{'mp3' if media_type == 'audio' else 'mp4'}"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)

    # ✅ YouTube download command with cookies
    command = [
        "yt-dlp",
        "--output", output_path,
        "--cookies", COOKIES_TXT,  # ✅ Using Netscape format cookies
        video_url
    ]

    if media_type == "audio":
        command.extend(["--extract-audio", "--audio-format", "mp3"])
    else:
        command.extend(["-f", "best"])  # Best video quality available

    try:
        subprocess.run(command, check=True)
        return jsonify({"file_url": f"https://vikasrajput-api.onrender.com/static/{unique_filename}", "message": "Download successful"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

# ✅ Static file serving
@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

# ✅ Keep Alive Route
@app.route('/keepalive', methods=['GET'])
def keep_alive():
    return "Server is alive!", 200

# ✅ YouTube Channel API
@app.route('/channel', methods=['GET'])
def get_channel():
    return jsonify({"channel_link": "https://m.youtube.com/mirrykal"})

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
