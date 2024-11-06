from flask import current_app as app
from PIL import Image, ImageDraw, ImageFont, ImageFile
import io
import cv2
import base64
import numpy as np

def extract_frames(video_path, start_time, duration=3):
    app.logger.info(f"Extracting frames from {video_path} starting at {start_time} for {duration} seconds")
    video = cv2.VideoCapture(video_path)
    
    fps = video.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_time * fps)
    end_frame = start_frame + int(duration * fps)

    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success or video.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
            break
        frames.append(frame)

    video.release()
    return frames

def select_key_frames(frames, max_images=9):
    total_frames = len(frames)
    
    # Define key moments in the swing (approximate percentages)
    key_moments = [0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.98, 1.0]
    
    selected_frames = []
    for moment in key_moments:
        frame_index = min(int(moment * total_frames), total_frames - 1)
        selected_frames.append(frames[frame_index])
    
    # If we need more frames, add some in between
    while len(selected_frames) < max_images:
        for i in range(len(selected_frames) - 1, 0, -1):
            if len(selected_frames) == max_images:
                break
            mid_frame = frames[(frame_indices[i] + frame_indices[i-1]) // 2]
            selected_frames.insert(i, mid_frame)
    
    # Convert frames to base64
    base64_frames = []
    for frame in selected_frames:
        _, buffer = cv2.imencode(".jpg", frame)
        base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
    
    return base64_frames

def detect_motion(frames):
    if len(frames) < 2:
        return []
    
    motion_scores = []
    for i in range(1, len(frames)):
        prev_frame = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        curr_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        
        flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        motion_score = np.mean(magnitude)
        motion_scores.append(motion_score)
    
    return motion_scores

def select_frames_smartly(frames, max_images=9):
    motion_scores = detect_motion(frames)
    
    # Normalize motion scores
    motion_scores = np.array(motion_scores)
    motion_scores = (motion_scores - np.min(motion_scores)) / (np.max(motion_scores) - np.min(motion_scores))
    
    # Select frames with highest motion, ensuring we include start and end
    selected_indices = [0, len(frames)-1]
    selected_indices.extend(np.argsort(motion_scores)[-max_images+2:][::-1])
    selected_indices = sorted(list(set(selected_indices)))[:max_images]
    
    selected_frames = [frames[i] for i in selected_indices]
    
    # Convert frames to base64
    base64_frames = []
    for frame in selected_frames:
        _, buffer = cv2.imencode(".jpg", frame)
        base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
    
    return base64_frames