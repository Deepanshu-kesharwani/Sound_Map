# SoundMap




A full-stack web application that provides music recommendations and allows users to search and play music using Last.fm and YouTube APIs. Built with FastAPI for the backend and Streamlit for the frontend.

## 🌟 Features

- **Music Search**: Search for any song or artist
- **Recommendations**: Get personalized music recommendations based on Last.fm data
- **YouTube Integration**: Play songs directly through embedded YouTube videos
- **Real-time Updates**: Dynamic content updates without page refresh
- **Caching**: Redis-based caching for improved performance
- **Responsive Design**: Mobile-friendly user interface

## 🛠️ Tech Stack

### Backend
- FastAPI (Python web framework)
- Redis (Caching)
- Last.fm API (Music data)
- YouTube Data API (Video playback)
- aiohttp (Async HTTP requests)

### Frontend
- Streamlit (Python web UI)
- Custom CSS
- Responsive design components
- Client-side caching

## 📋 Prerequisites

- Python 3.8 or higher
- Redis server
- Last.fm API key
- YouTube Data API key
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/music-discovery.git
cd music-discovery
```

2. **Set up environment variables**
Create a `.env` file in the backend directory:
```env
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_USERNAME=your_lastfm_username
YOUTUBE_API_KEY=your_youtube_api_key
REDIS_URL=redis://localhost
```

3. **Install Redis**
- Windows:
  - Download from https://github.com/microsoftarchive/redis/releases
  - Install and start Redis server


4. **Set up Backend**
```bash
cd backend
pip install -r backend-requirements.txt
```

5. **Set up Frontend**
```bash
cd frontend
pip install -r frontend-requirements.txt
```

## 🎯 Running the Application

1. **Start Redis Server** (if not already running)
```bash
# Windows
# Run redis-server.exe from installation directory
```

2. **Start Backend Server**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

3. **Start Frontend Application**
```bash
cd frontend
streamlit run app.py
```

4. **Access the Application**
- Frontend: http://localhost:8501
- Backend API docs: http://localhost:8000/docs

## 📝 API Documentation

### Endpoints

#### GET /recommendations
- Get music recommendations based on Last.fm data
- Query Parameters:
  - limit (optional): Number of recommendations to return (default: 10)

#### GET /search
- Search for songs
- Query Parameters:
  - query: Search term
  - limit (optional): Number of results to return (default: 10)

## 🔧 Configuration

### API Keys Setup

1. **Last.fm API**
- Create account at Last.fm
- Get API key from https://www.last.fm/api
- Add to .env file

2. **YouTube Data API**
- Create project in Google Cloud Console
- Enable YouTube Data API v3
- Create API credentials
- Add to .env file

## 🐛 Troubleshooting

1. **Redis Connection Issues**
- Verify Redis is running: `redis-cli ping`
- Check Redis port (default: 6379)
- Ensure REDIS_URL is correct in .env

2. **API Issues**
- Verify API keys are valid
- Check API quota limits
- Ensure proper network connectivity

3. **Application Errors**
- Check console logs
- Verify all dependencies are installed
- Ensure both servers are running

## 🔐 Security Notes

- Store API keys securely in .env file
- Don't commit .env file to version control
- Use appropriate CORS settings in production
- Implement rate limiting for production use

## 📦 Project Structure
```
music-discovery/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Backend dependencies
│   └── .env             # Environment variables
└── frontend/
    ├── app.py           # Streamlit application
    └── requirements.txt  # Frontend dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

- Last.fm for music data API
- YouTube for video playback
- FastAPI and Streamlit communities
