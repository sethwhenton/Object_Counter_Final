# AI Object Counting System

AI-powered application that counts objects in images using a sophisticated 3-step machine learning pipeline. Built for the AI Engineering Lab course at University of Passau.

## 🧠 How It Works

The application uses a sophisticated AI pipeline:

1. **Segmentation** - SAM (Segment Anything Model) breaks the image into distinct regions
2. **Classification** - ResNet-50 identifies what each segment contains  
3. **Mapping** - DistilBERT maps classifications to target object types

**Supported Object Types:** person, car, dog, cat, tree, building, motorcycle, bicycle, bus, bird, road, sky

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (tested with Python 3.13.7)
- MySQL 8.0+ (tested with MySQL 9.4.0)
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
python app_restructured.py
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
- **API Documentation**: http://localhost:5000/apidocs (Swagger UI)

## 📡 API Endpoints

### Core Endpoints

#### Health Check
```
GET /health
```
Returns API status, database connection, and system information

#### Object Types
```
GET /api/object-types
```
Returns all available object types for detection

#### Image Upload & Analysis
```
POST /api/count
```
**Body:** 
- `image` (file): Image to process
- `object_type` (string): Object type to count
- `description` (string, optional): Description of the image

**Response:**
```json
{
  "success": true,
  "result_id": "uuid-string",
  "object_type": "person",
  "predicted_count": 3,
  "total_segments": 15,
  "processing_time": 12.34,
  "image_path": "uploads/filename.jpg",
  "created_at": "2025-09-05T00:37:31"
}
```

#### Results Management
```
GET /api/results?page=1&per_page=10&object_type=person
```
Get paginated results with optional filtering

```
GET /api/results/{result_id}
```
Get detailed information for a specific result

```
PUT /api/correct
```
Submit corrections for AI predictions

```
DELETE /api/results/{result_id}
```
Delete a specific result

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
│   ├── app_restructured.py # Main Flask application (MySQL + RESTful API)
│   ├── storage/            # Custom database engine with UUID models
│   │   ├── engine/         # Database engine implementation
│   │   ├── base_model.py   # Base model with UUID primary keys
│   │   ├── inputs.py       # Input model for uploaded images
│   │   ├── object_types.py # Object type model
│   │   ├── outputs.py      # Output model for predictions
│   │   └── database_functions.py # Database operations
│   ├── models/             # AI pipeline models
│   │   └── pipeline.py     # AI pipeline implementation
│   ├── tests/              # Comprehensive test suite
│   │   ├── test_api/       # API endpoint tests
│   │   └── test_storage/   # Database tests
│   ├── uploads/            # User uploaded images
│   ├── requirements.txt    # Python dependencies
│   └── config.py           # Application configuration
├── frontend/               # React frontend
│   ├── src/                # React source code
│   │   ├── components/     # UI components
│   │   │   ├── ImageCounter.tsx      # Main upload interface
│   │   │   ├── ImageHistory.tsx      # History management
│   │   │   ├── ResultsDashboard.tsx  # Results display
│   │   │   └── ...                   # Other components
│   │   ├── services/       # API service layer
│   │   └── styles/         # CSS styles
│   ├── node_modules/       # Node.js dependencies
│   └── package.json        # Frontend dependencies
├── start_backend.bat       # Backend startup script (Windows)
├── start_frontend.bat      # Frontend startup script (Windows)
├── activate_venv.bat       # Virtual environment activation
├── requirements.txt        # Main Python dependencies
├── .gitlab-ci.yml         # CI/CD pipeline configuration
└── docs/                  # Documentation
    ├── API_DOCUMENTATION.md
    └── SETUP_AND_RUN.md
```

## 🔧 Development Status

### ✅ Completed Features
- **AI Pipeline**: Fully functional 3-step object counting pipeline
- **Flask Backend**: REST API with MySQL database, health checks, and performance monitoring
- **React Frontend**: Modern web interface with drag-and-drop upload, history management, and results dashboard
- **Database**: MySQL database with UUID-based models for storing results and corrections
- **Virtual Environment**: Complete Python environment setup with all dependencies
- **Performance Monitoring**: Real-time metrics and performance tracking
- **CI/CD Pipeline**: GitLab CI/CD with automated testing and deployment
- **Documentation**: Comprehensive setup and API documentation
- **Testing**: 44+ automated tests covering API and database functionality

### 🎯 Key Features
- **Image Upload**: Drag and drop interface for easy image upload
- **Object Selection**: Choose from 12 predefined object types
- **Real-time Results**: See counting results with confidence scores and processing times
- **History Tracking**: View previous uploads and results with pagination and filtering
- **Correction System**: Users can correct AI predictions and provide feedback
- **Performance Metrics**: Track system performance and processing times
- **Bulk Operations**: Select and delete multiple results at once
- **Detailed Views**: Click on results to see comprehensive analysis details

## 🛠️ Technologies

### Backend
- **Framework**: Flask 3.0.0 with Flask-RESTful
- **Database**: MySQL 8.0+ with custom UUID-based ORM
- **AI/ML**: PyTorch 2.8.0, Transformers 4.56.0, Segment Anything Model
- **Image Processing**: OpenCV, Pillow, NumPy
- **API Documentation**: Swagger/OpenAPI with Flasgger
- **Testing**: pytest with comprehensive test coverage

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components with modern design
- **Styling**: CSS with responsive design
- **State Management**: React hooks and context

### Development & DevOps
- **Virtual Environment**: Python venv with all dependencies
- **Package Management**: pip (Python), npm (Node.js)
- **Version Control**: Git with comprehensive .gitignore
- **CI/CD**: GitLab CI/CD with automated testing
- **Database**: MySQL with custom engine and UUID models

## 📋 Installation Details

The project comes with a pre-configured virtual environment containing:
- Flask 3.0.0 + Flask-CORS + Flask-RESTful + Flask-SQLAlchemy
- PyTorch 2.8.0 (CPU version) + TorchVision
- Transformers 4.56.0 + Accelerate
- OpenCV, Pillow, NumPy for image processing
- Segment Anything for AI pipeline
- PyMySQL for MySQL connectivity
- All other required dependencies

## 🗄️ Database Setup

### MySQL Configuration
The application uses MySQL with the following setup:
- **Development DB**: `obj_detect_dev_db`
- **Test DB**: `obj_detect_test_db`
- **User**: `obj_detect_dev`
- **Host**: `localhost`

### Database Initialization
The database is automatically initialized with 12 object types:
- person, car, dog, cat, tree, building
- motorcycle, bicycle, bus, bird, road, sky

## 🧪 Testing

### Running Tests
```bash
# Activate virtual environment
activate_venv.bat

# Run all tests
cd backend
python tests/test_runner.py --test all

# Run specific test suites
python tests/test_runner.py --test api      # API tests only
python tests/test_runner.py --test storage  # Database tests only
```

### Test Coverage
- **44+ Tests**: Comprehensive test suite
- **API Tests**: All endpoints and functionality
- **Database Tests**: Model operations and relationships
- **Integration Tests**: End-to-end workflows

## 🚀 CI/CD Pipeline

### GitLab CI/CD Features
- **Automated Testing**: Runs on every commit and merge request
- **Multi-stage Pipeline**: Test → Build → Deploy
- **MySQL Integration**: Automated database setup and testing
- **Artifact Management**: Test reports and build artifacts
- **Manual Deployment**: Controlled staging and production deployments

### Pipeline Stages
1. **Test**: Run comprehensive test suite
2. **Build**: Validate application and create artifacts
3. **Deploy**: Manual deployment to staging/production

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check MySQL service
python backend/check_mysql_service.py

# Test database connection
python backend/test_mysql_connection_fixed.py

# Initialize database
python backend/setup_mysql.py
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rmdir /s backend\venv
python -m venv backend/venv
activate_venv.bat
pip install -r requirements.txt
```

#### Frontend Issues
```bash
# Clear node modules and reinstall
cd frontend
rmdir /s node_modules
npm install
npm run dev
```

## 🎉 Ready to Use!

Your AI Object Counting System is fully set up and ready to use! The system includes:

- **AI Pipeline**: Object detection and counting using state-of-the-art models
- **Web Interface**: Modern React frontend with drag-and-drop image upload
- **Database**: MySQL database with UUID-based models for storing results and history
- **Performance Monitoring**: Real-time metrics and performance tracking
- **API**: RESTful API with Swagger documentation
- **CI/CD**: Automated testing and deployment pipeline

Just run the batch files or follow the manual setup instructions and start counting objects in your images! 🚀

## 📚 Additional Documentation

- `docs/API_DOCUMENTATION.md` - Complete API documentation
- `docs/SETUP_AND_RUN.md` - Detailed setup and troubleshooting guide
- `CI_CD_SETUP.md` - CI/CD pipeline setup and configuration
- `frontend/README.md` - Frontend-specific documentation
- `backend/PHASE_7_COMPLETION_SUMMARY.md` - Latest development updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python backend/tests/test_runner.py --test all`
5. Submit a pull request

## 📄 License

This project is developed for educational purposes as part of the AI Engineering Lab course at University of Passau.

---

**Built with ❤️ for AI Engineering Lab - University of Passau**