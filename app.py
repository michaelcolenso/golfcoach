"""GolfCoach API — FastAPI backend for AI golf swing analysis."""

import logging
import os
import tempfile
from pathlib import Path

import anyio
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ai_utils import analyze_swing
from frame_utils import extract_frames, select_frames_smartly
from schemas import AnalyzeResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 200 * 1024 * 1024
MAX_DURATION_SECONDS = 10.0
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-msvideo", "video/x-matroska"}

CLIENT_BUILD_DIR = Path(__file__).parent / "client" / "build"

app = FastAPI(title="GolfCoach API", version="1.0.0")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_video(
    video: UploadFile = File(...),
    start_time: float = Form(0.0),
    duration: float = Form(3.0),
) -> AnalyzeResponse:
    if video.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported video type: {video.content_type}")
    if not 0 < duration <= MAX_DURATION_SECONDS:
        raise HTTPException(status_code=422, detail=f"Duration must be between 0 and {MAX_DURATION_SECONDS} seconds")
    if start_time < 0:
        raise HTTPException(status_code=422, detail="start_time must be non-negative")

    suffix = Path(video.filename or "clip.mp4").suffix or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
        size = 0
        while chunk := await video.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                tmp.close()
                os.unlink(tmp_path)
                raise HTTPException(status_code=413, detail="Video exceeds the 200MB upload limit")
            tmp.write(chunk)

    logger.info("Processing %s (%.1f MB), start=%.2fs duration=%.2fs", video.filename, size / 1e6, start_time, duration)

    try:
        # Frame extraction and optical flow are CPU-bound; keep the event loop free.
        frames = await anyio.to_thread.run_sync(extract_frames, tmp_path, start_time, duration)
        if not frames:
            raise HTTPException(status_code=422, detail="No frames could be extracted — check the start time and video file")

        selected_frames = await anyio.to_thread.run_sync(select_frames_smartly, frames)
        feedback = await analyze_swing(selected_frames)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error processing video")
        raise HTTPException(status_code=500, detail="Error analyzing the video. Please try again.")
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass

    return AnalyzeResponse(
        filename=video.filename or "upload",
        frame_count=len(frames),
        selected_frames=selected_frames,
        feedback=feedback,
    )


# Serve the built SvelteKit SPA in production (client/build exists after `npm run build`).
if CLIENT_BUILD_DIR.is_dir():
    app.mount("/", StaticFiles(directory=CLIENT_BUILD_DIR, html=True), name="client")

    @app.exception_handler(404)
    async def spa_fallback(request: Request, exc: HTTPException):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": exc.detail}, status_code=404)
        return FileResponse(CLIENT_BUILD_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
