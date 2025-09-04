# 🗄️ TASK 2 Setup Guide: Database & API Integration

## 📦 Install New Dependencies

**Install database libraries:**
```powershell
py -m pip install Flask-SQLAlchemy SQLAlchemy PyMySQL
```

**Or install all at once:**
```powershell
py -m pip install -r requirements.txt
```

## 🗄️ Database Setup

### Option 1: SQLite (Recommended for Development)
**No additional setup required!** The app will automatically create `object_counting.db` file.

### Option 2: MySQL (Production)
**If you want to use MySQL:**

1. **Install MySQL Server**
2. **Create database:**
   ```sql
   CREATE DATABASE object_counting;
   ```
3. **Set environment variables:**
   ```powershell
   set DATABASE_TYPE=mysql
   set MYSQL_HOST=localhost
   set MYSQL_USER=root
   set MYSQL_PASSWORD=your_password
   set MYSQL_DATABASE=object_counting
   ```

## 🚀 Start the Enhanced API

```powershell
# Navigate to backend
cd backend

# Initialize database (first time only)
py init_db.py

# Start the server
py app.py
```

**Expected output:**
```
📦 Initializing object types...
✅ Created 9 object types!
✅ AI Pipeline initialized successfully!
Starting Object Counting API...
Available endpoints:
  GET  /health - Health check
  POST /test-pipeline - Test the AI pipeline
  POST /api/count - Production object counting
  PUT  /api/correct - Correct predictions
  GET  /api/results - Get all results
  GET  /api/object-types - Get available types
```

## 🧪 Test the New API

```powershell
# In a new terminal
py test_api_endpoints.py
```

**This will test:**
- ✅ Health check with database status
- ✅ Object types retrieval
- ✅ Production image upload & counting
- ✅ Prediction correction
- ✅ Results retrieval

## 📡 New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/count` | POST | Upload image, get count, save to DB |
| `/api/correct` | PUT | Correct a prediction |
| `/api/results` | GET | Get all results with pagination |
| `/api/object-types` | GET | Get available object types |

## 🗄️ Database Tables Created

- **object_types**: Available categories (car, cat, tree, etc.)
- **inputs**: Uploaded images and metadata  
- **outputs**: Predictions and user corrections

## 🎯 What's Different from Task 1

**Task 1:** AI pipeline only (no data persistence)
**Task 2:** AI pipeline + database + production API

**New features:**
- ✅ Data persistence in database
- ✅ Production-ready API endpoints
- ✅ User correction tracking
- ✅ Result history and pagination
- ✅ Robust error handling and validation

## 🔧 Troubleshooting

**"No module named 'flask_sqlalchemy'"**
```powershell
py -m pip install Flask-SQLAlchemy
```

**"Database connection failed"**
- Check if using SQLite (default) - no setup needed
- For MySQL: verify connection settings

**"Object type not found"**
- Run: `py init_db.py` to initialize object types

## 📊 Testing Results Format

**Production counting response:**
```json
{
  "success": true,
  "result_id": 1,
  "object_type": "car", 
  "predicted_count": 3,
  "total_segments": 10,
  "processing_time": 27.5,
  "image_path": "uploads/unique_filename.jpg",
  "created_at": "2025-09-02T10:30:00"
}
```

**Ready for Task 3: Frontend Development!** 🎨



