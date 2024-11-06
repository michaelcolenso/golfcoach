# GolfCoach - AI-Powered Golf Swing Analysis

![s-l1600](https://github.com/michaelcolenso/golfcoach/assets/778365/229ecd46-6e76-446f-97d2-fbba224a1116)

GolfCoach is an AI-powered application that analyzes golf swings from video uploads, providing detailed feedback and insights to improve your game. The application uses OpenAI's advanced AI models to analyze key frames from your swing and provide technical feedback.

## Features

- Video upload and playback interface
- Real-time swing analysis
- Frame-by-frame breakdown
- AI-powered swing feedback
- Interactive results display

## Tech Stack

### Backend
- Flask (Python web framework)
- OpenAI API for swing analysis
- OpenCV for video processing
- Flask-CORS for cross-origin support

### Frontend
- SvelteKit
- TailwindCSS for styling
- Custom video player controls
- Responsive design

## Prerequisites

- Python 3.7+
- Node.js 16+
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/michaelcolenso/golfcoach.git
cd golfcoach
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd client
npm install
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Running the Application

1. Start the Flask backend:
```bash
python app.py
```

2. In a separate terminal, start the frontend development server:
```bash
cd client
npm run dev
```

3. Visit `http://localhost:5173` in your browser to use the application.

## Usage

1. Upload a video of your golf swing using the upload interface
2. Use the video player to select the starting point of your swing
3. Click "Analyze" to receive AI-powered feedback
4. View the detailed analysis and recommendations on the results page

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
