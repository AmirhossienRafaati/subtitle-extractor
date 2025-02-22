import subprocess
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot
from telegram import InputFile

app = Flask(__name__)

# Telegram bot token (Replace this with your bot's token)
TELEGRAM_BOT_TOKEN = '7558810237:AAFDfVHQNtdbvx_QVAklBxsVsL7NTM0Q6EU'
CHANNEL_ID = '-1002252045082'  # Replace with your channel's username or ID

# Function to extract subtitles and return them
def extract_subtitles(video_url):
    # Prepare the ffmpeg command to extract subtitles
    command = [
        "ffmpeg", 
        "-y",  # Overwrite output file without asking
        "-i", video_url, 
        "-map", "0:s:0",  # Extract the first subtitle stream
        "-f", "srt",  # Force the subtitle format to SRT
        "pipe:1"  # Output to stdout (instead of a file)
    ]
    
    # Execute the command and capture the subtitle output in memory
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subtitles = result.stdout.decode()  # Decode the subtitle content from bytes to string
        return {"status": "success", "subtitles": subtitles}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error occurred: {e.stderr.decode()}"}


# Function to send subtitle file to Telegram channel asynchronously
async def upload_subtitles_to_telegram(subtitle_text):
    # Save the subtitle content to a file
    temp_file_path = "/tmp/subtitles.srt"
    with open(temp_file_path, 'w') as f:
        f.write(subtitle_text)

    # Initialize the Telegram bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Upload the subtitle file to the channel asynchronously
    with open(temp_file_path, 'rb') as subtitle_file:
        file = InputFile(subtitle_file, filename="subtitles.srt")
        message = await bot.send_document(chat_id=CHANNEL_ID, document=file)
        return message.message_id  # Return the message_id of the uploaded file


# API route to trigger subtitle extraction and upload to Telegram
@app.route('/extract_subtitles', methods=['POST'])
def extract_subtitles_api():
    # Get video URL from the request
    data = request.get_json()  # This expects JSON data
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"status": "error", "message": "Missing video_url parameter"}), 400

    # Call the subtitle extraction function
    result = extract_subtitles(video_url)

    if result["status"] == "success":
        # If subtitles were extracted successfully, upload to Telegram
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        message_id = loop.run_until_complete(upload_subtitles_to_telegram(result["subtitles"]))
        result["message_id"] = message_id  # Add message_id to the response

    # Return the result as a JSON response
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))  # Port from Heroku environment
