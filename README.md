# GolfCoach — AI-Powered Golf Swing Analysis

![s-l1600](https://github.com/michaelcolenso/golfcoach/assets/778365/229ecd46-6e76-446f-97d2-fbba224a1116)

GolfCoach analyzes golf swings from video uploads and gives detailed, frame-by-frame coaching feedback. Upload a clip, scrub to the start of your swing, and an AI coach breaks down every phase — setup through follow-through — with strengths, prioritized fixes, and practice drills.

## How it works

1. The selected clip window is decoded with OpenCV and sampled into frames.
2. Optical-flow motion scoring (computed on downscaled frames for speed) picks the most informative frames — the high-motion moments like the downswing and impact are always captured.
3. The key frames are sent to an OpenAI vision model via the Responses API with a **structured output schema**, so the analysis comes back as typed JSON (swing phase, observation, and tip per frame, plus strengths, recommendations, and drills) — no fragile text parsing.

## Tech stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) with async request handling (CPU-bound video work runs in a thread pool)
- OpenAI Responses API with Pydantic structured outputs
- OpenCV for frame extraction and optical-flow key-frame selection
- [uv](https://docs.astral.sh/uv/) for dependency management

**Frontend**
- Svelte 5 (runes) + SvelteKit 2, built as a static SPA
- Tailwind CSS v4
- Vite 8

## Prerequisites

- Python 3.11+
- Node.js 20+
- An OpenAI API key

## Setup

```bash
git clone https://github.com/michaelcolenso/golfcoach.git
cd golfcoach

# Backend dependencies (or: pip install -r requirements.txt)
uv sync

# Frontend dependencies
cd client && npm install && cd ..

# API key
export OPENAI_API_KEY='your-api-key-here'

# Optional: override the model (default: gpt-5-mini)
export OPENAI_MODEL='gpt-5-mini'
```

## Development

Run the backend and frontend in separate terminals:

```bash
# Terminal 1 — API on :8000
uv run uvicorn app:app --reload

# Terminal 2 — frontend on :5173 (proxies /api to :8000)
cd client && npm run dev
```

Visit http://localhost:5173.

## Production

Build the frontend, then run the backend — FastAPI serves the built SPA from `client/build`:

```bash
cd client && npm run build && cd ..
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000.

## API

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Health check |
| `/api/analyze` | POST | Multipart form: `video` (file, ≤200MB), `start_time` (seconds), `duration` (seconds, ≤10). Returns the selected frames (base64 JPEG) and a structured swing analysis. |

## Usage

1. Drag and drop (or browse for) a video of your golf swing
2. Scrub the player to the moment your swing starts — frame-step buttons help you get it exact
3. Pick a clip length and hit **Analyze my swing**
4. Review the frame-by-frame breakdown, strengths, recommendations, and drills

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License — see the LICENSE file for details.
