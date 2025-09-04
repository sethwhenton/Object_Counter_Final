# AI Object Counting System - Setup and Run Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ (✅ You have Python 3.13.7)
- Node.js 18+ (for frontend)
- Git

### 1. Backend Setup (Already Done!)

Your backend is already set up and ready to run! Here's what was installed:

#### Virtual Environment
- ✅ Created fresh virtual environment in `backend/venv/`
- ✅ Activated and upgraded pip

#### Dependencies Installed
- ✅ Flask 3.0.0 + Flask-CORS + Flask-SQLAlchemy
- ✅ PyTorch 2.8.0 (CPU version)
- ✅ Transformers 4.56.0
- ✅ OpenCV, Pillow, NumPy
- ✅ Segment Anything (for AI pipeline)
- ✅ All other required dependencies

### 2. Frontend Setup (Already Done!)

- ✅ Node.js dependencies installed
- ✅ React + TypeScript + Vite setup ready

## 🎯 How to Run the System

### Option 1: Use the Batch Files (Easiest)

1. **Start Backend**: Double-click `start_backend.bat`
   - This will activate the virtual environment and start the Flask server
   - Backend will run on: http://localhost:5000

2. **Start Frontend**: Double-click `start_frontend.bat`
   - This will start the React development server
   - Frontend will run on: http://localhost:3000

### Option 2: Manual Commands

#### Start Backend:
```bash
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

#### Start Frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

## 🌐 Access Your Application

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:5000
3. **Health Check**: http://localhost:5000/health

## 📋 Available API Endpoints

- `GET /health` - Health check
- `POST /test-pipeline` - Test the AI pipeline
- `POST /api/performance/start` - Start performance monitoring
- `POST /api/performance/stop` - Stop performance monitoring
- `GET /api/performance/metrics` - Get real-time metrics
- `POST /api/performance/update-stage` - Update processing stage
- `GET /api/performance/summary` - Get performance summary

## 🔧 Troubleshooting

### Backend Issues:
- If you see "No module named 'segment_anything'", run: `pip install segment-anything`
- If database issues occur, the app will create a new SQLite database automatically
- GPU monitoring is optional (shows warning if not available)

### Frontend Issues:
- Make sure Node.js is installed
- Run `npm install` in the frontend directory if needed

## 📁 Project Structure

```
├── backend/                 # Flask API server
│   ├── venv/               # Python virtual environment
│   ├── app.py              # Main Flask application
│   ├── models/             # Database and AI pipeline models
│   └── uploads/            # User uploaded images
├── frontend/               # React frontend
│   ├── src/                # React source code
│   ├── node_modules/       # Node.js dependencies
│   └── package.json        # Frontend dependencies
├── start_backend.bat       # Backend startup script
├── start_frontend.bat      # Frontend startup script
└── requirements.txt        # Python dependencies
```

## 🎉 You're Ready!

Your AI Object Counting System is now fully set up and ready to use! The system includes:

- **AI Pipeline**: Object detection and counting using state-of-the-art models
- **Web Interface**: Modern React frontend with drag-and-drop image upload
- **Database**: SQLite database for storing results and history
- **Performance Monitoring**: Real-time metrics and performance tracking
- **API**: RESTful API for integration with other systems

Just run the batch files and start counting objects in your images! 🚀

