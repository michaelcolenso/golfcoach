# CLAUDE.md - AI Assistant Guide for GolfCoach

## Project Overview

**GolfCoach** is an AI-powered golf swing analysis application that processes video uploads and provides detailed technical feedback using OpenAI's GPT-4o vision model. The application combines computer vision techniques with AI coaching to help golfers improve their swing mechanics.

### Tech Stack
- **Backend**: Flask (Python) with OpenAI API integration
- **Frontend**: SvelteKit with TailwindCSS and Skeleton UI
- **Video Processing**: OpenCV with optical flow motion detection
- **AI Model**: GPT-4o (vision-capable) for swing analysis

---

## Repository Structure

```
golfcoach/
├── app.py                      # Main Flask application and API endpoints
├── frame_utils.py              # Video processing and frame extraction
├── api_utils.py                # OpenAI API integration
├── response_parser.py          # Parse AI responses into structured data
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata (Python 3.10+)
├── uv.lock                    # Dependency lock file (UV package manager)
├── .gitignore                 # Git ignore patterns
│
├── client/                    # SvelteKit frontend application
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +page.svelte          # Home/upload page
│   │   │   ├── +page.server.js       # Server-side logic
│   │   │   ├── +layout.svelte        # Layout wrapper
│   │   │   └── results/
│   │   │       └── +page.svelte      # Results display page
│   │   ├── lib/                      # Shared components (INCOMPLETE)
│   │   │   ├── VideoUploader.svelte  # File upload component
│   │   │   ├── VideoPlayer.svelte    # Video player with timeline
│   │   │   ├── UploadButton.svelte   # Upload trigger button
│   │   │   └── stores/
│   │   │       └── resultsStore.js   # Svelte store for results
│   │   ├── app.html                  # Root HTML template
│   │   └── app.pcss                  # PostCSS/Tailwind entry
│   ├── static/                       # Static assets
│   │   └── videos/                   # Temporary video storage
│   ├── package.json                  # Node dependencies
│   ├── svelte.config.js              # SvelteKit configuration
│   ├── vite.config.js                # Vite bundler config
│   ├── tailwind.config.cjs           # Tailwind/Skeleton UI config
│   └── postcss.config.cjs            # PostCSS configuration
│
├── templates/                 # Legacy Flask templates (being phased out)
│   ├── index.html
│   └── results.html
└── static/                    # Legacy static files
    └── src/
        └── input.css
```

---

## Core Architecture

### Request Flow: Video Upload → AI Analysis → Results

```
┌─────────────────────────────────────────────────────────────────┐
│ USER WORKFLOW                                                    │
└─────────────────────────────────────────────────────────────────┘

1. Frontend (SvelteKit)
   ├─ User uploads video file
   ├─ Previews video in VideoPlayer component
   ├─ Selects start time by scrubbing timeline
   └─ Clicks "Analyze" button

2. POST /upload → Flask Backend
   ├─ Receives: FormData(video, start_time, duration=3)
   ├─ Saves video temporarily to client/public/videos/
   └─ Initiates processing pipeline

3. Frame Extraction (frame_utils.py)
   ├─ extract_frames(video_path, start_time, 3s)
   ├─ Uses OpenCV to read video
   ├─ Calculates frame range from FPS
   └─ Returns list of frame matrices (~90 frames at 30fps)

4. Motion Detection & Frame Selection (frame_utils.py)
   ├─ detect_motion(frames)
   │  ├─ Converts frames to grayscale
   │  ├─ Computes optical flow (Farneback algorithm)
   │  └─ Returns motion intensity scores
   ├─ select_frames_smartly(frames, max_images=9)
   │  ├─ Normalizes motion scores (0-1)
   │  ├─ Selects 9 frames with highest motion
   │  ├─ Ensures start/end frames included
   │  └─ Converts to base64 JPEG encoding
   └─ Returns 9 base64-encoded frames

5. OpenAI API Call (api_utils.py)
   ├─ call_openai_api(selected_frames)
   ├─ Model: gpt-4o (vision-capable)
   ├─ Prompt: "Review each image and determine what element of the
   │          golf swing it is. Using your knowledge of golf,
   │          provide useful feedback to the golfer as if you
   │          were the coach"
   ├─ Max tokens: 2500
   └─ Returns OpenAI completion object

6. Response Parsing (response_parser.py)
   ├─ parse_golf_text(description)
   ├─ Splits by numbered sections (Image 1, Image 2, ...)
   ├─ Extracts swing phases (Setup, Backswing, Downswing, etc.)
   ├─ Extracts recommendations using regex
   └─ Returns structured JSON:
       {
         swing_analysis: { image_1: "...", image_2: "..." },
         swing_phases: { setup: "...", backswing: "..." },
         recommendations: ["...", "..."],
         overall_feedback: "..."
       }

7. Cleanup & Response
   ├─ Deletes uploaded video file (os.remove)
   └─ Returns JSON with feedback + selected_frames

8. Frontend Results Display
   ├─ Stores results in resultsStore (Svelte store)
   ├─ Navigates to /results page
   └─ Displays frames + feedback in grid layout
```

---

## Key Files Deep Dive

### Backend Files

#### `app.py` (Main Flask Application)
**Location**: `/home/user/golfcoach/app.py`

**Responsibilities**:
- Flask app initialization with CORS enabled
- Serves SvelteKit frontend
- Handles video upload endpoint

**Key Routes**:
- `GET /` - Serves client/app.html
- `GET /<path>` - Serves static assets from client/public/
- `POST /upload` - Main video processing endpoint
  - Parameters: `video` (file), `start_time` (float), `duration` (float, default=3)
  - Returns: JSON with feedback, frame_count, selected_frames

**Configuration**:
- Port: 5000
- Debug mode: enabled in development
- OpenAI API key: from `OPENAI_API_KEY` environment variable
- Logging: INFO level with Flask logger

**Error Handling**:
- 400: Missing file or no file selected
- 500: File save errors or video processing errors
- All errors return JSON with `error` and `exception` fields

#### `frame_utils.py` (Video Processing)
**Location**: `/home/user/golfcoach/frame_utils.py`

**Functions**:

1. **`extract_frames(video_path, start_time, duration=3)`**
   - Uses OpenCV (cv2.VideoCapture)
   - Calculates frame range: `start_frame = start_time * fps`
   - Extracts all frames in time window
   - Returns: List of frame matrices (BGR format)

2. **`detect_motion(frames)`**
   - Converts frames to grayscale
   - Computes dense optical flow using `cv2.calcOpticalFlowFarneback()`
   - Parameters: pyr_scale=0.5, levels=3, winsize=15, iterations=3
   - Calculates flow magnitude using `cv2.cartToPolar()`
   - Returns: List of motion scores (mean magnitude per frame)

3. **`select_frames_smartly(frames, max_images=9)`**
   - Motion-based intelligent frame selection
   - Normalizes motion scores to [0, 1]
   - Always includes first and last frames
   - Selects remaining frames by highest motion scores
   - Encodes frames as JPEG → base64 strings
   - Returns: List of base64-encoded images (max 9)

4. **`select_key_frames(frames, max_images=9)`** *(Alternative method - less used)*
   - Pre-defined key moments: [0%, 20%, 40%, 60%, 80%, 90%, 95%, 98%, 100%]
   - Fixed-position frame selection
   - Returns: Base64-encoded frames

**Dependencies**:
- OpenCV (cv2): Video I/O, optical flow
- NumPy: Array operations, statistical functions
- Pillow (PIL): Image manipulation
- base64: Frame encoding for API transmission

#### `api_utils.py` (OpenAI Integration)
**Location**: `/home/user/golfcoach/api_utils.py`

**Function**: `call_openai_api(selected_frames)`
- Uses OpenAI Chat Completions API
- Model: `gpt-4o` (vision-capable)
- Max tokens: 2500
- Message structure:
  ```python
  {
    "role": "user",
    "content": [
      "I have provided a number of images from a video of a golf swing...",
      {"image": frame1, "resize": 768},
      {"image": frame2, "resize": 768},
      ...
    ]
  }
  ```
- Prompt engineering: Acts as golf coach, provides phase identification + feedback
- Error handling: Logs exceptions and re-raises
- Returns: OpenAI completion object

**Important**: Images are resized to 768px for API efficiency

#### `response_parser.py` (AI Response Processing)
**Location**: `/home/user/golfcoach/response_parser.py`

**Function**: `parse_golf_text(text)`
- Splits response by numbered sections: `\n\n\d+\. `
- Extracts swing phases using regex: `^(Setup|Backswing|Downswing|Impact|Follow-through):`
- Extracts recommendations: `Recommendation:?\s*(.*?)(?:\n|$)`
- Builds structured dictionary:
  ```python
  {
    'swing_analysis': {'image_1': '...', 'image_2': '...'},
    'swing_phases': {'setup': '...', 'backswing': '...'},
    'recommendations': ['...'],
    'overall_feedback': '...'
  }
  ```
- Returns: Parsed dictionary for frontend consumption

### Frontend Files

#### `client/src/routes/+page.svelte` (Home/Upload Page)
**Location**: `/home/user/golfcoach/client/src/routes/+page.svelte`

**State Management**:
- `videoFile`: Selected file object
- `videoUrl`: Object URL for preview
- `currentTime`: Current video position (seconds)
- `startTime`: Selected analysis start point
- `maxDuration`: Video duration
- `isLoading`: Writable store for loading state
- `errorMessage`: Writable store for error messages

**Component Dependencies** (Not yet implemented):
- `VideoUploader.svelte` - File selection UI
- `VideoPlayer.svelte` - Custom video player with timeline
- `UploadButton.svelte` - Upload trigger button
- `resultsStore` - Shared store for results

**Event Handlers**:
- `handleFileSelected(event)`: Creates object URL from file
- `handleTimeChange(event)`: Updates currentTime
- `handleUpload()`: Async function that:
  1. Creates FormData with video, start_time, duration
  2. POSTs to `http://127.0.0.1:5000/upload`
  3. Stores result in resultsStore
  4. Navigates to `/results` on success

**Styling**: Uses Skeleton UI's hero component + TailwindCSS utilities

#### `client/src/routes/results/+page.svelte` (Results Display)
**Location**: `/home/user/golfcoach/client/src/routes/results/+page.svelte`

**Data Flow**:
- Subscribes to `resultsStore` on mount
- Redirects to `/` if no results available
- Displays loading state until results arrive

**Layout**:
- Grid: 1 column mobile, 2 columns desktop (`grid-cols-1 md:grid-cols-2`)
- Each frame: Image (left) + Feedback (right)
- Sections: Swing Analysis → Recommendations → Overall Feedback

**Data Binding**:
- Frames: `results.selected_frames` (base64 images)
- Feedback: `results.feedback.swing_analysis.image_N`
- Recommendations: `results.feedback.recommendations[]`
- Overall: `results.feedback.overall_feedback`

---

## Development Workflows

### Local Development Setup

#### Prerequisites
- Python 3.10+ (required by pyproject.toml)
- Node.js 16+
- OpenAI API key with GPT-4o access

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Run Flask server (port 5000)
python app.py
```

#### Frontend Setup
```bash
cd client

# Install Node dependencies
npm install

# Run Vite dev server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### Full Stack Development
The frontend dev server proxies API requests to the Flask backend at `http://127.0.0.1:5000`.

**Terminal 1** (Backend):
```bash
python app.py
```

**Terminal 2** (Frontend):
```bash
cd client && npm run dev
```

Access the app at: `http://localhost:5173`

### Common Development Tasks

#### Adding New Analysis Features
1. **Modify the OpenAI prompt** in `api_utils.py:14`
2. **Update response parsing** in `response_parser.py` to extract new data
3. **Update frontend display** in `client/src/routes/results/+page.svelte`

#### Changing Frame Selection Logic
- Edit `frame_utils.py:select_frames_smartly()`
- Adjust `max_images` parameter (default: 9)
- Consider API token limits when increasing frame count

#### Modifying Video Processing
- Duration: Change default in `app.py:52` (currently 3 seconds)
- Motion detection parameters: Adjust in `frame_utils.py:64` (optical flow)
- Frame quality: Change JPEG encoding in `frame_utils.py:88`

#### Styling Changes
- Global styles: `client/src/app.pcss`
- Tailwind config: `client/tailwind.config.cjs`
- Skeleton UI theme: Modify `data-theme` in `client/src/app.html`

---

## Code Conventions & Patterns

### Python Backend

**Import Organization**:
1. Standard library (os, base64, logging)
2. Third-party packages (flask, cv2, openai)
3. Local modules (frame_utils, api_utils, response_parser)

**Logging**:
- Use Flask's logger: `app.logger.info()`, `app.logger.error()`
- Log level: INFO (set in `app.py:17`)
- Log key operations: file saves, API calls, processing steps

**Error Handling**:
- Use try-except blocks for I/O and API calls
- Always clean up resources in `finally` blocks (e.g., video deletion)
- Return JSON errors with HTTP status codes (400, 500)

**Function Naming**:
- Descriptive names: `extract_frames()`, `detect_motion()`, `call_openai_api()`
- Snake_case for Python functions and variables

**File Handling**:
- Use `secure_filename()` from werkzeug for uploaded files
- Create directories with `os.makedirs(..., exist_ok=True)`
- Always delete temporary files after processing

### Frontend (SvelteKit)

**Component Structure**:
- `<script>` → `<template>` → `<style>` order
- Use `let` for component state
- Use `writable()` stores for shared state

**Naming Conventions**:
- Components: PascalCase (VideoUploader.svelte)
- Variables: camelCase (videoUrl, currentTime)
- Event handlers: handle* prefix (handleUpload, handleFileSelected)

**Styling Approach**:
- Utility-first with TailwindCSS
- Skeleton UI components for common patterns
- Scoped styles in `<style>` tags for component-specific CSS

**Data Flow**:
- Props down, events up pattern
- Use Svelte stores for cross-page state (resultsStore)
- Use `goto()` for programmatic navigation

**Async Operations**:
- Use async/await for API calls
- Set loading states before async operations
- Handle errors with try-catch and error messages

---

## Configuration Files Reference

### Python Configuration

| File | Purpose | Key Settings |
|------|---------|--------------|
| **requirements.txt** | Python dependencies | Flask, openai, opencv-python-headless, flask-cors |
| **pyproject.toml** | Project metadata | Python >=3.10, project name/version |
| **uv.lock** | Dependency lock | UV package manager lock file |

### Frontend Configuration

| File | Purpose | Key Settings |
|------|---------|--------------|
| **package.json** | Node dependencies | SvelteKit, Vite, TailwindCSS, Skeleton UI |
| **svelte.config.js** | SvelteKit config | Adapter settings, preprocessor config |
| **vite.config.js** | Vite bundler | SvelteKit plugin, dev server settings |
| **tailwind.config.cjs** | Tailwind CSS | Skeleton UI theme, content paths |
| **postcss.config.cjs** | PostCSS | Tailwind + autoprefixer plugins |

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| **OPENAI_API_KEY** | Yes | OpenAI API authentication (GPT-4o access) |

---

## API Integration Details

### OpenAI API Usage

**Model**: GPT-4o (vision-capable)
- Supports multi-image inputs
- Max context: Multiple high-res images
- Output: Up to 2500 tokens

**Cost Considerations**:
- Each analysis processes 9 frames
- Images resized to 768px for efficiency
- Average analysis: ~2000 tokens output

**Rate Limits**:
- Depends on OpenAI account tier
- Consider implementing request queuing for production

**Error Scenarios**:
1. Invalid API key → 401 error
2. Rate limit exceeded → 429 error
3. Model unavailable → 503 error
4. Token limit exceeded → 400 error

**Prompt Engineering Tips**:
- Current prompt focuses on swing phase identification + coaching feedback
- To modify output format, update prompt in `api_utils.py:14`
- Consider adding few-shot examples for more structured output

---

## Testing Strategy

### Current State
- No automated tests currently implemented
- Manual testing workflow:
  1. Upload test golf swing video
  2. Verify frame extraction
  3. Check API response
  4. Validate results display

### Testing Recommendations for AI Assistants

#### Backend Testing
```python
# Suggested test structure (not yet implemented)
# tests/test_frame_utils.py
def test_extract_frames():
    frames = extract_frames('test_video.mp4', 0, 3)
    assert len(frames) > 0
    assert frames[0].shape[2] == 3  # BGR format

def test_motion_detection():
    # Test with static vs. moving frames
    pass

def test_frame_selection():
    # Ensure start/end frames always included
    pass
```

#### Frontend Testing
- Consider Playwright for E2E testing
- Test file upload flow
- Test video player controls
- Test results display with mock data

#### Integration Testing
- Mock OpenAI API responses
- Test full upload → analysis → results flow
- Verify error handling paths

---

## Deployment Considerations

### Backend Deployment

**Production Settings**:
- Disable Flask debug mode: `app.run(debug=False)`
- Use production WSGI server (Gunicorn, uWSGI)
- Set secure CORS origins (currently allows all)
- Add authentication for API endpoints
- Implement request rate limiting

**Environment**:
- Set `OPENAI_API_KEY` via secure secret management
- Configure logging to file/service
- Set up error monitoring (Sentry, etc.)

**File Storage**:
- Current: Temporary local storage with immediate deletion
- Production: Consider cloud storage (S3) for video uploads
- Clean up orphaned files with scheduled task

### Frontend Deployment

**Build Process**:
```bash
cd client
npm run build
```

**Static Hosting Options**:
- Vercel (SvelteKit adapter-auto compatible)
- Netlify
- CloudFlare Pages
- Traditional web server (nginx + SPA routing)

**Environment Variables**:
- Update API endpoint from `http://127.0.0.1:5000` to production URL
- Use SvelteKit environment variables ($env/static/public)

### Infrastructure

**Recommended Stack**:
- Backend: Docker container with Python 3.10+
- Frontend: Static hosting with CDN
- API Gateway: Handle CORS, rate limiting, authentication
- Video Storage: S3 or equivalent object storage
- Monitoring: Application performance monitoring (APM)

---

## Git Workflow & Branch Management

### Branch Naming Convention
- Feature branches: `claude/feature-name-sessionId`
- Example: `claude/add-claude-documentation-BmBnf`
- Always develop on designated feature branches
- Never push directly to main/master

### Commit Message Style
- Concise, descriptive messages
- Focus on "why" rather than "what"
- Examples from history:
  - "Merge pull request #1 from michaelcolenso/moonshot"
  - "fixed the scrolling and its all working now."
  - "works"

### Git Commands
```bash
# Check current status
git status

# Create and switch to feature branch
git checkout -b claude/feature-name-sessionId

# Stage and commit changes
git add .
git commit -m "Descriptive commit message"

# Push to remote (with retry on network errors)
git push -u origin claude/feature-name-sessionId
```

---

## Common Pitfalls & Solutions

### Issue: Missing Frontend Components
**Symptom**: `VideoUploader.svelte`, `VideoPlayer.svelte`, etc. not found
**Cause**: Components referenced but not yet implemented
**Solution**: Create components in `client/src/lib/` directory

### Issue: OpenAI API Errors
**Symptom**: 401 Unauthorized or API call failures
**Cause**: Missing or invalid `OPENAI_API_KEY`
**Solution**: Export environment variable before running Flask app

### Issue: CORS Errors
**Symptom**: Browser blocks API requests from frontend
**Cause**: Cross-origin restrictions
**Current Solution**: Flask-CORS enables all origins
**Production Solution**: Restrict CORS to specific origins

### Issue: Video Processing Slow
**Symptom**: Long wait times for analysis results
**Cause**: Processing all frames in 3-second window (~90 frames)
**Solution**: Already optimized with motion-based frame selection (9 frames)

### Issue: Large Response Payload
**Symptom**: Slow network transfer of results
**Cause**: Base64 images in JSON response
**Solution**: Consider returning image URLs instead of base64 data

---

## Tips for AI Assistants

### Understanding the Codebase

1. **Start with the flow**: Follow `app.py` → `frame_utils.py` → `api_utils.py` → `response_parser.py`
2. **Frontend follows backend**: Results page structure matches API response structure
3. **Incomplete frontend**: Many components are referenced but not implemented
4. **Legacy code exists**: `templates/` and `static/` are from earlier Flask-only version

### Making Changes

#### When modifying video processing:
- Test with various video formats (MP4, MOV, etc.)
- Verify OpenCV can read the file format
- Consider frame rate variations (30fps, 60fps)
- Monitor memory usage with large videos

#### When modifying AI prompts:
- Test with multiple swing videos
- Verify response parser handles new output format
- Update frontend if response structure changes
- Consider token limits (max 2500)

#### When adding features:
- Follow existing patterns (Flask routes, Svelte components)
- Update both backend and frontend together
- Add error handling for new failure modes
- Document changes in comments

### Code Reading Tips

1. **Python files are well-structured**: Each file has clear responsibility
2. **OpenCV operations**: `frame_utils.py:64` uses Farneback optical flow (common CV technique)
3. **Base64 encoding**: Required for embedding images in JSON responses
4. **Svelte reactivity**: `$isLoading` syntax auto-subscribes to writable stores
5. **File cleanup**: Always happens in `finally` block (`app.py:79-83`)

### Common Patterns

**Backend Error Response**:
```python
return jsonify({'error': 'Error message', 'exception': str(e)}), 500
```

**Frontend Async Handler**:
```javascript
async function handleAction() {
  isLoading.set(true);
  try {
    // API call
  } catch (error) {
    errorMessage.set('Error message');
  } finally {
    isLoading.set(false);
  }
}
```

**Frame Processing Pipeline**:
```
Video → Extract all frames → Detect motion → Select top 9 → Encode base64
```

---

## Resources & References

### Documentation Links
- **Flask**: https://flask.palletsprojects.com/
- **SvelteKit**: https://kit.svelte.dev/docs
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **OpenCV**: https://docs.opencv.org/
- **TailwindCSS**: https://tailwindcss.com/docs
- **Skeleton UI**: https://www.skeleton.dev/

### Key Dependencies

#### Backend (Python)
- Flask 3.x - Web framework
- openai 1.x - OpenAI API client
- opencv-python-headless - Computer vision (no GUI)
- Pillow - Image manipulation
- numpy - Numerical operations

#### Frontend (Node)
- @sveltejs/kit 2.x - Full-stack framework
- svelte 4.x - UI components
- vite 5.x - Build tool and dev server
- tailwindcss 3.x - Utility CSS
- @skeletonlabs/skeleton 2.x - Component library

### Golf Swing Terminology

Understanding these terms helps when working with the AI analysis:

- **Setup/Address**: Initial stance before swing begins
- **Backswing**: Club moving away from ball, rotating back
- **Top of Swing**: Transition point, club at highest position
- **Downswing**: Club moving toward ball
- **Impact**: Club contacts ball
- **Follow-through**: Continuation after impact
- **Finish**: Final pose/position

---

## Appendix: Project Status

### Implemented Features
- ✅ Video upload with file validation
- ✅ Frame extraction from video
- ✅ Motion-based intelligent frame selection
- ✅ OpenAI GPT-4o integration for swing analysis
- ✅ Structured response parsing
- ✅ Results display with images and feedback
- ✅ Responsive design (mobile + desktop)

### In Progress / Incomplete
- ⚠️ Frontend components (VideoUploader, VideoPlayer, UploadButton)
- ⚠️ Svelte stores (resultsStore)
- ⚠️ Error handling UI improvements
- ⚠️ Loading states and animations

### Future Enhancements (Not Implemented)
- ❌ User authentication
- ❌ Video history/storage
- ❌ Comparison between swings
- ❌ Drill/exercise recommendations
- ❌ Progress tracking over time
- ❌ Multiple video formats support verification
- ❌ Automated testing suite
- ❌ Production deployment configuration
- ❌ Caching of analysis results
- ❌ Batch video processing

### Known Issues
1. Components imported in +page.svelte are not yet implemented
2. Legacy templates exist but are not used
3. No authentication on API endpoints
4. CORS allows all origins (security concern for production)
5. Video files temporarily stored on disk (not scalable)
6. No rate limiting on API calls
7. No error recovery for failed OpenAI API calls

---

## Quick Start for AI Assistants

### First Time Working on This Repo

1. **Read the flow diagram** (section: Core Architecture)
2. **Understand the 3 main backend files**: `app.py`, `frame_utils.py`, `api_utils.py`
3. **Check the frontend routes**: `+page.svelte` (upload) and `results/+page.svelte` (display)
4. **Note the incomplete components**: Many imports won't resolve yet

### Before Making Changes

1. **Read the relevant file** completely
2. **Check dependencies**: What other files import this file?
3. **Understand the data flow**: What format is input/output?
4. **Test locally**: Set up environment and test the change

### When Adding Features

1. **Start with backend**: API endpoint → processing logic → response format
2. **Update frontend**: Add display logic for new data
3. **Test the full flow**: Upload → process → display
4. **Document changes**: Update this CLAUDE.md if architecture changes

---

## Version History

- **v0.1.0** - Initial release with basic swing analysis
- **Current** - Active development, transitioning from Flask templates to SvelteKit

---

## Contact & Support

- **Repository**: https://github.com/michaelcolenso/golfcoach
- **Issues**: Report bugs via GitHub Issues
- **License**: MIT License

---

*Last Updated: 2026-01-07*
*Document Version: 1.0.0*
*Generated for AI Assistant Reference*
