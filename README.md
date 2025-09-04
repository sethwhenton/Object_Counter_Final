# AI Object Counting System

AI-powered application that counts objects in images using a sophisticated 3-step machine learning pipeline. Built for the AI Engineering Lab course at University of Passau.

## 🧠 How It Works

The application uses a sophisticated AI pipeline:

1. **Segmentation** - SAM (Segment Anything Model) breaks the image into distinct regions
2. **Classification** - ResNet-50 identifies what each segment contains  
3. **Mapping** - DistilBERT maps classifications to target object types

**Supported Object Types:** car, cat, tree, dog, building, person, sky, ground, hardware

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ (tested with Python 3.13.7)
- Node.js 18+ (for frontend)
- Git

### Option 1: Use Batch Files (Windows - Easiest)

1. **Start Backend**: Double-click `start_backend.bat`
   - This will activate the virtual environment and start the Flask server
   - Backend will run on: http://localhost:5000

2. **Start Frontend**: Double-click `start_frontend.bat`
   - This will start the React development server
   - Frontend will run on: http://localhost:3000

### Option 2: Manual Setup

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate

# Start the Flask server
python app.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns API status and system information

### Test Pipeline  
```
POST /test-pipeline
```
**Body:** 
- `image` (file): Image to process
- `object_type` (string): Object type to count

**Response:**
```json
{
  "success": true,
  "object_type": "car",
  "predicted_count": 3,
  "total_segments": 15,
  "processing_time": 12.34
}
```

### Performance Monitoring
- `POST /api/performance/start` - Start performance monitoring
- `POST /api/performance/stop` - Stop performance monitoring
- `GET /api/performance/metrics` - Get real-time metrics
- `POST /api/performance/update-stage` - Update processing stage
- `GET /api/performance/summary` - Get performance summary

## 🏗️ Project Structure

```
├── backend/                 # Flask API server
│   ├── venv/               # Python virtual environment (ready to use)
│   ├── app.py              # Main Flask application
│   ├── models/             # Database and AI pipeline models
│   │   ├── database.py     # Database models and operations
│   │   └── pipeline.py     # AI pipeline implementation
│   ├── uploads/            # User uploaded images
│   ├── requirements.txt    # Python dependencies
│   └── config.py           # Application configuration
├── frontend/               # React frontend
│   ├── src/                # React source code
│   │   ├── components/     # UI components
│   │   ├── services/       # API service layer
│   │   └── styles/         # CSS styles
│   ├── node_modules/       # Node.js dependencies
│   └── package.json        # Frontend dependencies
├── start_backend.bat       # Backend startup script (Windows)
├── start_frontend.bat      # Frontend startup script (Windows)
├── requirements.txt        # Main Python dependencies
├── .gitignore             # Git ignore rules
└── SETUP_AND_RUN.md       # Detailed setup guide
```

## 🔧 Development Status

### ✅ Completed Features
- **AI Pipeline**: Fully functional 3-step object counting pipeline
- **Flask Backend**: REST API with health checks and performance monitoring
- **React Frontend**: Modern web interface with drag-and-drop upload
- **Database**: SQLite database for storing results and corrections
- **Virtual Environment**: Complete Python environment setup
- **Performance Monitoring**: Real-time metrics and performance tracking
- **Documentation**: Comprehensive setup and API documentation

### 🎯 Key Features
- **Image Upload**: Drag and drop interface for easy image upload
- **Object Selection**: Choose from predefined object types
- **Real-time Results**: See counting results with confidence scores
- **History Tracking**: View previous uploads and results
- **Correction System**: Users can correct AI predictions
- **Performance Metrics**: Track system performance and processing times

## 🛠️ Technologies

### Backend
- **Framework**: Flask 3.0.0
- **AI/ML**: PyTorch 2.8.0, Transformers 4.56.0, Segment Anything Model
- **Database**: SQLite (development), MySQL ready (production)
- **Image Processing**: OpenCV, Pillow, NumPy
- **Testing**: pytest with coverage reporting

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components with modern design
- **Styling**: CSS with responsive design

### Development
- **Virtual Environment**: Python venv with all dependencies
- **Package Management**: pip (Python), npm (Node.js)
- **Version Control**: Git with comprehensive .gitignore

## 📋 Installation Details

The project comes with a pre-configured virtual environment containing:
- Flask 3.0.0 + Flask-CORS + Flask-SQLAlchemy
- PyTorch 2.8.0 (CPU version) + TorchVision
- Transformers 4.56.0 + Accelerate
- OpenCV, Pillow, NumPy for image processing
- Segment Anything for AI pipeline
- All other required dependencies

## 🎉 Ready to Use!

Your AI Object Counting System is fully set up and ready to use! The system includes:

- **AI Pipeline**: Object detection and counting using state-of-the-art models
- **Web Interface**: Modern React frontend with drag-and-drop image upload
- **Database**: SQLite database for storing results and history
- **Performance Monitoring**: Real-time metrics and performance tracking
- **API**: RESTful API for integration with other systems

Just run the batch files or follow the manual setup instructions and start counting objects in your images! 🚀

## 📚 Additional Documentation

- `SETUP_AND_RUN.md` - Detailed setup and troubleshooting guide
- `backend/API_DOCUMENTATION.md` - Complete API documentation
- `frontend/README.md` - Frontend-specific documentation