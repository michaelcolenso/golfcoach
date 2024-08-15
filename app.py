from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from frame_utils import extract_frames, select_frames_uniformly, create_thumbnail_sequence
from api_utils import call_openai_api
from response_parser import parse_golf_text
import cv2
import openai
import base64
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='client/public')
CORS(app)

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
    duration = request.form.get('duration', default=5, type=float)
    app.logger.info(request.form)

    try:
        frames = extract_frames(filepath, start_time, duration)
        frame_count = len(frames)
        
        selected_frames = select_frames_uniformly(frames, max_images=9)

        openai_response = call_openai_api(selected_frames)
        
        if openai_response is not None:
            description = openai_response.choices[0].message.content
            image_feedback = parse_golf_text(description)
        else:
            description = "Failed to call OpenAI API or process the response"
            image_feedback = {}

        thumbnail = create_thumbnail_sequence(selected_frames)
        thumbnail_base64 = base64.b64encode(thumbnail).decode('utf-8')

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
        'thumbnail': thumbnail_base64
    }

    return jsonify(context)

if __name__ == '__main__':
    app.run(debug=True, port=5000)