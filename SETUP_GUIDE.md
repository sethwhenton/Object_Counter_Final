# AI Object Counting System - Setup Guide

## 🚀 Quick Setup (Recommended)

### **Option 1: Automated Setup**
```bash
python setup_development_environment.py
```

### **Option 2: Manual Setup**
```bash
# 1. Activate virtual environment
activate_venv.bat

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Setup MySQL databases
python backend/setup_mysql.py

# 4. Test connection
python backend/test_mysql_connection_fixed.py
```

## 📋 Requirements

### **System Requirements**
- **Python 3.8+** (tested with Python 3.13.7)
- **MySQL 8.0+** (tested with MySQL 9.4.0)
- **Node.js 18+** (for frontend)
- **Windows 10/11** (current setup)

### **Python Dependencies**
All dependencies are listed in `requirements.txt`:

#### **Core Framework**
- `Flask==3.0.0` - Web framework
- `Flask-CORS==4.0.0` - Cross-origin resource sharing
- `Flask-RESTful==0.3.10` - RESTful API framework

#### **AI/ML Libraries**
- `torch>=2.6.0` - PyTorch deep learning framework
- `torchvision>=0.19.0` - Computer vision utilities
- `transformers>=4.40.0` - Hugging Face transformers
- `accelerate>=1.10.0` - Model acceleration
- `huggingface-hub>=0.34.3` - Model hub access

#### **Image Processing**
- `Pillow>=11.3.0` - Image manipulation
- `opencv-python>=4.12.0.88` - Computer vision
- `numpy>=2.2.6` - Numerical computing
- `scikit-image>=0.25.2` - Advanced image processing
- `scipy>=1.15.3` - Scientific computing

#### **Database**
- `SQLAlchemy>=2.0.23` - Database ORM
- `PyMySQL>=1.1.0` - MySQL connector (Windows compatible)
- `cryptography>=3.4.8` - Encryption for MySQL authentication

#### **API & Documentation**
- `flasgger==0.9.7.1` - Swagger documentation
- `marshmallow==4.0.1` - Object serialization

#### **Utilities**
- `requests>=2.32.4` - HTTP library
- `python-dotenv>=1.0.0` - Environment variables
- `PyYAML>=6.0.2` - YAML parsing
- `tqdm>=4.67.1` - Progress bars

#### **Testing**
- `pytest>=7.4.3` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting

## 🔧 Virtual Environment Management

### **Activate Virtual Environment**
```bash
# Windows
activate_venv.bat

# Or manually
cd backend
.\venv\Scripts\activate
```

### **Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Deactivate Virtual Environment**
```bash
deactivate
```

## 🗄️ MySQL Database Setup

### **Prerequisites**
- MySQL 8.0+ installed
- MySQL service running
- Root access to MySQL

### **Setup Databases**
```bash
python backend/setup_mysql.py
```

This creates:
- `obj_detect_dev_db` - Development database
- `obj_detect_test_db` - Test database
- Database users with proper permissions

### **Test Connection**
```bash
python backend/test_mysql_connection_fixed.py
```

## 🚀 Running the Application

### **Backend (Flask API)**
```bash
# Activate virtual environment first
activate_venv.bat

# Start backend
python backend/app.py
```

### **Frontend (React)**
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### **Test MySQL Connection**
```bash
python backend/test_mysql_connection_fixed.py
```

### **Test API Endpoints**
```bash
python backend/test_api_endpoints.py
```

### **Run All Tests**
```bash
pytest backend/tests/
```

## 🔧 Troubleshooting

### **MySQL Issues**
1. **Service not running:**
   ```bash
   python backend/check_mysql_service.py
   ```

2. **Install MySQL service:**
   ```bash
   python backend/install_mysql_service.py
   ```

3. **Manual service start:**
   ```bash
   net start mysql
   ```

### **Python Dependencies**
1. **Reinstall requirements:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

### **Virtual Environment Issues**
1. **Recreate virtual environment:**
   ```bash
   rmdir /s backend\venv
   python -m venv backend/venv
   ```

2. **Activate and reinstall:**
   ```bash
   activate_venv.bat
   pip install -r requirements.txt
   ```

## 📁 Project Structure

```
├── backend/                 # Flask API server
│   ├── venv/               # Python virtual environment
│   ├── storage/            # Custom database engine
│   │   ├── engine/         # Database engine
│   │   ├── base_model.py   # Base model with UUID
│   │   ├── inputs.py       # Input model
│   │   ├── object_types.py # Object type model
│   │   └── outputs.py      # Output model
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
├── requirements.txt        # Main requirements
├── setup_development_environment.py # Automated setup
├── activate_venv.bat       # Virtual environment activation
└── SETUP_GUIDE.md          # This file
```

## 🎯 Development Workflow

1. **Activate virtual environment:** `activate_venv.bat`
2. **Start MySQL service:** `python backend/check_mysql_service.py`
3. **Start backend:** `python backend/app.py`
4. **Start frontend:** `cd frontend && npm run dev`
5. **Test changes:** `python backend/test_mysql_connection_fixed.py`

## 📞 Support

If you encounter issues:
1. Check this setup guide
2. Run the automated setup: `python setup_development_environment.py`
3. Check MySQL service status: `python backend/check_mysql_service.py`
4. Test connection: `python backend/test_mysql_connection_fixed.py`


