from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from frame_utils import extract_frames, select_frames_uniformly
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

# Route to add static files (CSS and JS)
@app.route("/<path:path>")
def base(path):
    return send_from_directory('client/public', path)

@app.route('/upload', methods=['POST'])
def upload_video():
    # Ensure a file is present in the request
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['video']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.static_folder, 'videos', filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        # Save the file to the filesystem
        file.save(filepath)
    except Exception as e:
        # Handle exceptions that could occur during file save
        return jsonify({'error': 'Failed to save file', 'exception': str(e)}), 500

    # Retrieve start time and duration from the request
    start_time = request.form.get('start_time', default=0, type=float)
    duration = request.form.get('duration', default=3, type=float)
    app.logger.info(request.form)

    try:
        # Process the video and extract frames
        frames = extract_frames(filepath, start_time, duration)
        # app.logger.info(f"START TIME: {start_time}, DURATION: {duration}")
        frame_count = len(frames)  # Count the number of frames extracted
        
        # Call OpenAI API with the extracted frames
       
        selected_frames = select_frames_uniformly(frames, max_images=6)  # Adjust max_images as needed

        openai_response = call_openai_api(selected_frames)
        
        if openai_response is not None:
            # Access the 'choices' attribute only if the response is not None
            description = openai_response.choices[0].message.content
            image_feedback = parse_golf_text(description)
        else:
            # If the response is None, set an appropriate description
            description = "Failed to call OpenAI API or process the response"
    finally:
        # Attempt to remove the saved video file after processing, in a finally block to ensure it's always executed
        try:
            os.remove(filepath)
        except FileNotFoundError:
            # File was already deleted or never saved, handle as needed
            pass

    # Return the response to the client
    context = {
        'selected_frames': selected_frames,
        'message': 'File uploaded and processed successfully',
        'filename': filename,
        'feedback': image_feedback,
        'frame_count': frame_count  # Include the frame count in the response
    }

    return jsonify(context);


if __name__ == '__main__':
    app.run(debug=True, port=5000)
