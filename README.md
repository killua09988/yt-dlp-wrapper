# yt-dlp-wrapper

A simple web wrapper for yt-dlp with Python Flask backend and basic HTML frontend.

## 🚀 Live Demo

**Deployed on Render:** [https://yt-dlp-wrapper.onrender.com](https://yt-dlp-wrapper.onrender.com)

## 📋 API Usage

### Download Video Endpoint

**POST** `/download`

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Example using curl:**
```bash
curl -X POST https://yt-dlp-wrapper.onrender.com/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Response:**
The API will return the video file for download.

## 🏃‍♂️ Running Locally

### Prerequisites
- Python 3.7+
- pip
- ffmpeg (for video processing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/killua09988/yt-dlp-wrapper.git
   cd yt-dlp-wrapper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server:**
   ```bash
   cd backend
   python app.py
   ```

4. **Access the application:**
   - Open your browser and go to `http://localhost:5000`
   - Or use the API endpoint directly at `http://localhost:5000/download`

### Dependencies (requirements.txt)

The project uses the following Python packages:
- Flask - Web framework
- yt-dlp - YouTube video downloader
- ffmpeg-python - Video processing

## 📁 Project Structure

```
yt-dlp-wrapper/
├── frontend/           # HTML, CSS, JavaScript files
├── backend/            # Flask application
│   ├── app.py         # Main Flask application
│   └── requirements.txt # Python dependencies
└── README.md          # Project documentation
```

## 🔧 Features

- Simple web interface for video downloads
- RESTful API endpoint
- Support for YouTube and other platforms via yt-dlp
- Lightweight Flask backend
- Easy deployment on cloud platforms

## 📝 Description

This project provides a web-based interface for yt-dlp, allowing users to download videos through a simple HTML frontend. The backend is built with Python Flask to handle video download requests and serves both the web interface and API endpoints.

### Frontend
The frontend folder contains the HTML, CSS, and JavaScript files for the web interface, providing an intuitive user experience for video downloads.

### Backend
The backend folder contains the Python Flask application and related server-side code, including the main API endpoint for processing download requests.

---
created with Comet Assistant
