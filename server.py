from flask import Flask, request, send_file, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)
STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/download", methods=["GET"])
def download():
    url = request.args.get("url")
    file_type = request.args.get("type", "audio")  # Default: audio
    
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400
    
    unique_id = uuid.uuid4().hex  # Generate unique filename
    
    if file_type == "video":
        output_file = f"{STATIC_FOLDER}/{unique_id}.mp4"
        yt_dlp_cmd = [
            "yt-dlp", "-f", "bestvideo+bestaudio", "--merge-output-format", "mp4", "-o", output_file, url
        ]
    else:
        output_file = f"{STATIC_FOLDER}/{unique_id}.mp3"
        yt_dlp_cmd = [
            "yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "-o", output_file, url
        ]
    
    try:
        subprocess.run(yt_dlp_cmd, check=True)
        return send_file(output_file, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Download failed", "details": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
