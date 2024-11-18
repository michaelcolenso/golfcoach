from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import google.generativeai as genai
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='client/public')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Ensure GOOGLE_API_KEY is set in environment variables

# Allowed video MIME types
ALLOWED_MIME_TYPES = {
    'video/mp4',
    'video/mpeg',
    'video/mov',
    'video/avi',
    'video/x-flv',
    'video/mpg',
    'video/webm',
    'video/wmv',
    'video/3gpp'
}

@app.route('/')
def client():
    return send_from_directory('client', 'app.html')

@app.route("/<path:path>")
def base(path):
    return send_from_directory('client/public', path)

def allowed_file(mimetype):
    return mimetype in ALLOWED_MIME_TYPES

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.mimetype):
        return jsonify({'error': f'Unsupported file type: {file.mimetype}'}), 400

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(app.static_folder, 'videos')
    filepath = os.path.join(upload_folder, filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        # Save the uploaded file to the server
        file.save(filepath)
        logger.info(f"File saved to {filepath}")

        # Upload the video using the File API
        logger.info("Uploading file to Google Gemini File API...")
        video_file = genai.upload_file(path=filepath)
        logger.info(f"Upload initiated. File URI: {video_file.uri}")

        # Poll the file state until it's ACTIVE or FAILED
        logger.info("Polling file state...")
        while video_file.state.name == "PROCESSING":
            logger.info("File is processing...")
            time.sleep(10)  # Wait for 10 seconds before checking again
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            logger.error("File processing failed.")
            return jsonify({'error': 'File processing failed.'}), 500
        
        logger.info("File is active and ready for inference.")

        # Retrieve the prompt from the request, default if not provided
        # prompt = request.form.get('prompt', "Analyze the video and provide a summary.")

        # Choose the Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Make the LLM inference request
        logger.info("Making LLM inference request...")
        response = model.generate_content([video_file, "analyze the golfers swing. provide direct feedback on each component of the golf swing."], request_options={"timeout": 600})

        logger.info("Inference completed.")

        # Optionally, delete the file after processing to save storage
        # video_file.delete()
        # logger.info("Uploaded file deleted after processing.")

        return jsonify({'response': response.text}), 200

    except Exception as e:
        logger.exception("An error occurred during video upload and processing.")
        return jsonify({'error': 'Failed to process the video', 'exception': str(e)}), 500

if __name__ == '__main__':
    # Ensure the server reloads on code changes and runs in debug mode for development
    app.run(debug=True, port=5000)
