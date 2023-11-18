from flask import Flask, request, jsonify, send_from_directory
import cv2
import openai
import base64
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

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

    try:
        # Process the video and extract frames
        frames = extract_frames(filepath)
        frame_count = len(frames)  # Count the number of frames extracted
        
        # Call OpenAI API with the extracted frames
        openai_response = call_openai_api(frames)
        
        if openai_response is not None:
            # Access the 'choices' attribute only if the response is not None
            description = openai_response.choices[0].message.content
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
    return jsonify({
        'message': 'File uploaded and processed successfully',
        'filename': filename,
        'description': description,
        'frame_count': frame_count  # Include the frame count in the response
    })

def extract_frames(video_path):
    video = cv2.VideoCapture(video_path)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames

def call_openai_api(base64_frames):
    # Construct the payload with the frames as base64 encoded images
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "I have provided a number of images from a video of a golf swing. Review each image and determine what element of the golf swing it is. Using your knowledge of golf, provide useful feedback to the golfer as if you were the coach",
                *map(lambda x: {"image": x, "resize": 768}, base64_frames[1::90]),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 1000,
    }

    try:
        result = openai.ChatCompletion.create(**params)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
