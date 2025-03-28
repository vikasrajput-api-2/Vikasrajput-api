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
COOKIES_JSON = "cookies.json"
COOKIES_TXT = "cookies.txt"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

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

def delete_old_files():
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        if os.path.isfile(file_path) and time.time() - os.path.getctime(file_path) > 20:
            os.remove(file_path)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get("url")
    type_ = request.args.get("type", "audio")
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    delete_old_files()
    convert_cookies()
    
    unique_filename = f"{uuid.uuid4()}.mp3" if type_ == "audio" else f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
    
    command = [
        "yt-dlp",
        "-f", "bestaudio/best" if type_ == "audio" else "best",
        "--extract-audio" if type_ == "audio" else "--recode-video",
        "mp3" if type_ == "audio" else "mp4",
        "--output", output_path,
        "--cookies", COOKIES_TXT,
        url
    ]
    
    try:
        print("▶ Running command:", " ".join(command))
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
                                                                                                                                                                               
