# Golf Swing Analyzer - Client-Side AI Analysis

A fully automated, client-side web application that analyzes golf swing videos using AI-powered pose detection and provides professional coaching feedback.

## Features

- **100% Client-Side Processing**: All video analysis happens in your browser - no backend server required
- **AI Pose Detection**: Uses TensorFlow.js with MoveNet for accurate body pose detection
- **Automatic Key Frame Extraction**: Identifies three critical swing moments:
  - Setup Position
  - Top of Backswing
  - Impact Position
- **Professional AI Analysis**: Powered by Google's Gemini AI for detailed swing feedback
- **Privacy-First**: Your videos never leave your device
- **Beautiful UI**: Modern, responsive design with drag-and-drop upload

## Quick Start

### 1. Get a Gemini API Key (Free)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (starts with `AIza...`)

### 2. Open the Application

Simply open `golf-analyzer.html` in a modern web browser:

```bash
# Option 1: Double-click the file in your file explorer

# Option 2: Use a local server (recommended for best performance)
python -m http.server 8000
# Then visit: http://localhost:8000/golf-analyzer.html

# Option 3: Using Node.js
npx serve .
# Then visit the URL shown
```

### 3. Use the Application

1. **Enter your Gemini API key** in the input field at the top
2. **Upload a golf swing video** (MP4, MOV, or WebM format)
3. **Wait for analysis** - the app will:
   - Load and analyze your video
   - Detect body poses in each frame
   - Identify the three key swing moments
   - Extract and annotate those frames
   - Send them to Gemini AI for professional analysis
4. **View results** - see the extracted poses and detailed coaching feedback

## How It Works

### 1. Pose Detection

The application uses **MoveNet Thunder** (TensorFlow.js) to detect 17 body keypoints in each video frame:
- Head, shoulders, elbows, wrists
- Hips, knees, ankles
- And more...

### 2. Swing Phase Identification

The app analyzes pose data to automatically identify the three key moments:

**Setup Position:**
- Detected in the first 30% of the video
- Looks for stable stance with wrists in ready position
- High confidence pose detection

**Top of Backswing:**
- Detected in the middle 40-70% of the video
- Identifies maximum wrist height
- Peak shoulder rotation
- Maximum coil position

**Impact Position:**
- Detected in the final 40% of the video
- Finds the moment when the club contacts the ball
- Looks for wrists coming down from backswing
- Forward weight transfer

### 3. AI Analysis

The three extracted frames are sent to **Gemini 1.5 Flash** with a professional coaching prompt that analyzes:
- Stance and posture
- Body alignment
- Weight transfer
- Shoulder rotation
- Club position
- Common swing faults
- Specific improvement recommendations

## Technical Details

### Technologies Used

- **TensorFlow.js**: ML framework for browser-based AI
- **MoveNet**: State-of-the-art pose detection model
- **Gemini API**: Google's multimodal AI for image analysis
- **HTML5 Canvas**: Video frame extraction and pose visualization
- **Vanilla JavaScript**: No framework dependencies

### Browser Requirements

- Modern browser with WebGL support (Chrome, Firefox, Safari, Edge)
- Minimum 4GB RAM recommended
- JavaScript enabled
- Internet connection (for loading libraries and Gemini API)

### Performance

- Typical processing time: 30-60 seconds for a 10-second video
- Processes ~90 frames for comprehensive pose detection
- Uses client-side GPU acceleration when available
- No video file size limits (all processing is local)

## Privacy & Security

- **All video processing happens locally** in your browser
- Your video files are never uploaded to any server
- Only the three extracted frames are sent to Gemini API for analysis
- API key is stored only in memory (not saved)
- No data collection or tracking

## Troubleshooting

### "Could not detect any poses"
- Ensure the golfer is clearly visible in the frame
- Check that the video quality is good
- Make sure the full body is visible in most frames
- Try recording from a side angle

### "Failed to get analysis from Gemini API"
- Verify your API key is correct
- Check that you have API quota remaining (free tier has limits)
- Ensure you have internet connectivity
- Try again in a few moments if rate-limited

### Slow Performance
- Close other browser tabs to free up memory
- Use a shorter video clip (5-10 seconds ideal)
- Try using Chrome for best performance
- Ensure your device meets minimum requirements

### "Please upload a valid video file"
- Use MP4, MOV, or WebM formats
- Ensure the file is not corrupted
- Try converting the video to MP4 with a tool like HandBrake

## Video Recording Tips

For best results:
- **Record from the side** (90-degree angle to the golfer)
- **Include full body** from head to feet
- **Use good lighting** - avoid shadows and backlighting
- **Keep camera stable** - use a tripod if possible
- **Record at least one complete swing**
- **Keep video short** - 5-10 seconds is ideal
- **Ensure clear background** - avoid cluttered backgrounds

## Comparison with Original Application

This new client-side analyzer differs from the original GolfCoach application:

| Feature | Original (Flask/OpenAI) | New (Client-Side/Gemini) |
|---------|------------------------|--------------------------|
| Architecture | Backend required | 100% client-side |
| Processing | Server-side | Browser-based |
| AI Model | OpenAI GPT-4 Vision | Google Gemini |
| Frame Extraction | User selects time range | Automatic pose detection |
| Key Frames | 9 frames | 3 specific poses |
| Privacy | Videos uploaded to server | Videos stay on device |
| Setup | Python + Node.js | Just open HTML file |
| Dependencies | Many packages | None (CDN-loaded) |

## Future Enhancements

Potential improvements:
- [ ] Compare swing to professional golfers
- [ ] Video side-by-side comparison
- [ ] Export analysis as PDF
- [ ] Track progress over time
- [ ] Slow-motion playback with pose overlay
- [ ] Club path tracking
- [ ] Swing speed calculation
- [ ] Mobile app version

## API Costs

**Gemini API Pricing** (as of 2025):
- Free tier: 15 requests per minute
- Each analysis = 1 request with 3 images
- More than enough for personal use
- Paid tiers available for high volume

**Note**: This is significantly more cost-effective than OpenAI's vision API while providing comparable quality.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- **TensorFlow.js** - Google
- **MoveNet** - Google Research
- **Gemini API** - Google AI
- Built with assistance from Claude (Anthropic)

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Ensure you're using a supported browser
3. Verify your Gemini API key is valid
4. Try with a different video file

---

**Enjoy improving your golf swing with AI-powered analysis!** ⛳
