from flask import Flask, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import os
import re

app = Flask(__name__)
CORS(app)  

def sanitize_filename(title):
    return re.sub(r'[\/:*?"<>|]', '', title)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()

    url = data.get('url')
    quality = data.get('quality')
    folder_path = data.get('folder_path')
    selected_format = data.get('format')

    try:
        yt = YouTube(url)
        video_title = yt.title
        sanitized_title = sanitize_filename(video_title)

        video_streams = yt.streams.filter(file_extension="mp4", res=quality, progressive=True)

        if not video_streams:
            return jsonify({"error": "No MP4 streams available for the specified quality."}), 500

        video = video_streams.first()

        output_path = os.path.join(folder_path, sanitized_title)

        if selected_format == 'mp4':
            video.download(output_path=output_path, filename=sanitized_title + '.mp4')
        elif selected_format == 'mp3':
            audio = yt.streams.filter(only_audio=True).first()
            audio.download(output_path=output_path, filename=sanitized_title + '.mp3')

        return jsonify({"message": "Download completed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
