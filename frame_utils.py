from flask import current_app as app
from PIL import Image, ImageDraw, ImageFont, ImageFile
import io
import cv2
import base64
import math

def extract_frames(video_path, start_time, duration=5):
    app.logger.info(f"Extracting frames from {video_path} starting at {start_time} for {duration} seconds")
    video = cv2.VideoCapture(video_path)
    
    fps = video.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_time * fps)
    end_frame = start_frame + int(duration * fps)

    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success or video.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    return base64Frames

def select_frames_uniformly(base64_frames, max_images):
    total_frames = len(base64_frames)
    step = max(1, total_frames // max_images)
    app.logger.info(f"Step: {step}")
    selected_frames = base64_frames[0::step][:max_images]
    return selected_frames

def create_thumbnail_sequence(selected_frames):
    thumbnails = []

    for base64_frame in selected_frames:
        frame_pil = Image.open(io.BytesIO(base64.b64decode(base64_frame)))
        thumbnails.append(frame_pil)

    width, height = thumbnails[0].size

    thumbnail_image = Image.new('RGB', (width * len(thumbnails), height))

    for i, thumbnail in enumerate(thumbnails):
        thumbnail_image.paste(thumbnail, (i * width, 0))

    img_byte_arr = io.BytesIO()
    ImageFile.MAXBLOCK = thumbnail_image.size[0] * thumbnail_image.size[1]
    thumbnail_image.save(img_byte_arr, format='PNG', optimize=True)

    if img_byte_arr.tell() > 20 * 1024 * 1024:
        thumbnail_image = thumbnail_image.resize((width // 2, height // 2))
        img_byte_arr = io.BytesIO()
        thumbnail_image.save(img_byte_arr, format='PNG', optimize=True)

    thumbnail = img_byte_arr.getvalue()

    return thumbnail