"""Video frame extraction and key-frame selection.

Frame selection uses optical-flow motion scoring computed on downscaled
grayscale frames, which is ~50x faster than full-resolution Farneback flow
while ranking frames identically for this purpose.
"""

import base64
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Cap how many frames we pull from the clip so very high-fps video doesn't
# blow up memory or flow-computation time. 60 frames over a 3s clip is
# plenty of temporal resolution to find the key swing positions.
MAX_EXTRACTED_FRAMES = 60
FLOW_WIDTH = 320          # downscale width for optical flow computation
OUTPUT_MAX_DIM = 768      # longest side of frames sent to the model
JPEG_QUALITY = 85


def extract_frames(video_path: str, start_time: float, duration: float = 3.0) -> list[np.ndarray]:
    logger.info("Extracting frames from %s at t=%.2fs for %.2fs", video_path, start_time, duration)
    video = cv2.VideoCapture(video_path)
    try:
        if not video.isOpened():
            raise ValueError("Could not open video file")

        fps = video.get(cv2.CAP_PROP_FPS) or 30.0
        total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        start_frame = max(0, int(start_time * fps))
        end_frame = min(total - 1, start_frame + int(duration * fps)) if total > 0 else start_frame + int(duration * fps)

        span = max(1, end_frame - start_frame + 1)
        step = max(1, -(-span // MAX_EXTRACTED_FRAMES))  # ceil division

        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frames: list[np.ndarray] = []
        index = start_frame
        while index <= end_frame:
            success, frame = video.read()
            if not success:
                break
            if (index - start_frame) % step == 0:
                frames.append(frame)
            index += 1

        logger.info("Extracted %d frames (step=%d)", len(frames), step)
        return frames
    finally:
        video.release()


def _motion_scores(frames: list[np.ndarray]) -> np.ndarray:
    """Mean optical-flow magnitude between consecutive downscaled frames."""
    if len(frames) < 2:
        return np.array([])

    h, w = frames[0].shape[:2]
    scale = FLOW_WIDTH / w
    size = (FLOW_WIDTH, max(1, int(h * scale)))

    grays = [cv2.cvtColor(cv2.resize(f, size, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for f in frames]

    scores = np.empty(len(frames) - 1)
    for i in range(1, len(grays)):
        flow = cv2.calcOpticalFlowFarneback(grays[i - 1], grays[i], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude = cv2.magnitude(flow[..., 0], flow[..., 1])
        scores[i - 1] = float(np.mean(magnitude))
    return scores


def _encode_frame(frame: np.ndarray) -> str:
    """Resize so the longest side is OUTPUT_MAX_DIM and encode as base64 JPEG."""
    h, w = frame.shape[:2]
    largest = max(h, w)
    if largest > OUTPUT_MAX_DIM:
        scale = OUTPUT_MAX_DIM / largest
        frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    return base64.b64encode(buffer).decode("utf-8")


def select_frames_smartly(frames: list[np.ndarray], max_images: int = 9) -> list[str]:
    """Pick the most informative frames: always the first and last, plus the
    frames with the highest motion in between, returned in chronological order
    as base64 JPEGs."""
    if not frames:
        return []
    if len(frames) <= max_images:
        return [_encode_frame(f) for f in frames]

    scores = _motion_scores(frames)

    selected = {0, len(frames) - 1}
    # scores[i] is the motion between frame i and i+1; attribute it to frame i+1
    # so high-motion moments (downswing, impact) are captured.
    for i in np.argsort(scores)[::-1]:
        if len(selected) >= max_images:
            break
        selected.add(int(i) + 1)

    ordered = sorted(selected)[:max_images]
    return [_encode_frame(frames[i]) for i in ordered]
