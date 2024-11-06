from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from frame_utils import extract_frames, select_frames_smartly
from api_utils import call_openai_api
from response_parser import parse_golf_text
import cv2
import openai
import base64
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='client/public')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def client():
    return send_from_directory('client', 'app.html')

@app.route("/<path:path>")
def base(path):
    return send_from_directory('client/public', path)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.static_folder, 'videos', filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': 'Failed to save file', 'exception': str(e)}), 500

    start_time = request.form.get('start_time', default=0, type=float)
    duration = request.form.get('duration', default=3, type=float)
    logger.info(f"Processing video: {filename}, start_time: {start_time}, duration: {duration}")

    try:
        frames = extract_frames(filepath, start_time, duration)
        frame_count = len(frames)
        
        selected_frames = select_frames_smartly(frames, max_images=9)

        openai_response = call_openai_api(selected_frames)
        
        if openai_response is not None:
            logger.info("OpenAI API Response:")
            logger.info(openai_response)
            description = openai_response.choices[0].message.content
            image_feedback = parse_golf_text(description)
            logger.info("Parsed Golf Text:")
            logger.info(image_feedback)
        else:
            description = "Failed to call OpenAI API or process the response"
            image_feedback = {}
            logger.error("Failed to get response from OpenAI API")

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': 'Error processing video', 'exception': str(e)}), 500

    finally:
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    context = {
        'message': 'File uploaded and processed successfully',
        'filename': filename,
        'feedback': image_feedback,
        'frame_count': frame_count,
        'selected_frames': selected_frames
    }

    return jsonify(context)

if __name__ == '__main__':
    app.run(debug=True, port=5000)