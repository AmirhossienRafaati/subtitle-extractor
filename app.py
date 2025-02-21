import subprocess
import os
from flask import Flask, request, jsonify


app = Flask(__name__)

def extract_subtitles(video_url, output_dir):
    # Prepare the ffmpeg command to extract subtitles
    command = [
        "ffmpeg", 
        "-y",  # Overwrite output file without asking
        "-i", video_url, 
        "-map", "0:s:0",  # Extract the first subtitle stream
        f"{output_dir}/subtitles.srt"
    ]
    
    # Execute the command
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {"status": "success", "message": f"Subtitles extracted successfully! Output: {result.stdout.decode()}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error occurred: {e.stderr.decode()}"}

# API route to trigger subtitle extraction
@app.route('/extract_subtitles', methods=['POST'])
def extract_subtitles_api():
    # Get video URL and output directory from request
    data = request.get_json()  # This expects JSON data
    video_url = data.get('video_url')
    output_dir = data.get('output_dir', '/tmp')  # Default output directory in Heroku is /tmp

    if not video_url:
        return jsonify({"status": "error", "message": "Missing video_url parameter"}), 400

    # Call the subtitle extraction function
    result = extract_subtitles(video_url, output_dir)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))  # Port from Heroku environment
