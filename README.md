# Object Counting Application

AI-powered application that counts objects in images using a 3-step machine learning pipeline.

## 🧠 How It Works

The application uses a sophisticated AI pipeline:

1. **Segmentation** - SAM (Segment Anything Model) breaks the image into distinct regions
2. **Classification** - ResNet-50 identifies what each segment contains  
3. **Mapping** - DistilBERT maps classifications to target object types

**Supported Object Types:** car, cat, tree, dog, building, person, sky, ground, hardware

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Setup & Run

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Run automated setup:**
   ```bash
   # Windows
   py setup.py
   
   # Mac/Linux
   python setup.py
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux  
   source venv/bin/activate
   ```

4. **Start the API server:**
   ```bash
   # Windows
   py app.py
   
   # Mac/Linux
   python app.py
   ```

5. **Test the pipeline:**
   ```bash
   # In a new terminal (Windows)
   py test_pipeline.py
   
   # Mac/Linux
   python test_pipeline.py
   ```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns API status

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

## 🏗️ Project Structure

```
backend/
├── app.py              # Flask application
├── models/
│   └── pipeline.py     # AI pipeline implementation
├── requirements.txt    # Python dependencies
├── setup.py           # Automated setup script
└── test_pipeline.py   # API test script
```

## 🔧 Development

The project is structured in 3 main phases:

1. **✅ TASK 1: Core AI Pipeline** - Convert Jupyter notebook to Flask service
2. **🔄 TASK 2: Database & API** - Add MySQL database and proper REST endpoints  
3. **⏳ TASK 3: Frontend & Testing** - Web interface and comprehensive testing

## 🎯 Next Steps

- Add MySQL database integration
- Implement `/api/count` and `/api/correct` endpoints
- Build web frontend
- Add comprehensive testing

## 🛠️ Technologies

- **Backend:** Flask, Python
- **AI/ML:** PyTorch, Transformers, Segment Anything Model
- **Database:** MySQL (planned)
- **Frontend:** TBD (React/Vue/Angular)
