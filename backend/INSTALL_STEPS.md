# 🚀 Manual Installation Steps

## ✅ You have Python working! 
Use `py` instead of `python` on your Windows system.

## 📦 Install Dependencies

**Option 1: One by one (safest)**
```powershell
py -m pip install Flask
py -m pip install Flask-CORS  
py -m pip install torch
py -m pip install torchvision
py -m pip install transformers
py -m pip install Pillow
py -m pip install numpy
py -m pip install requests
```

**Option 2: All at once**
```powershell
py -m pip install Flask Flask-CORS torch torchvision transformers Pillow numpy requests
```

## 🧪 Test the Installation

1. **Start the API:**
   ```powershell
   py app.py
   ```

2. **Test with sample image:** (open new terminal)
   ```powershell
   py test_pipeline.py
   ```

## 🔧 If Something Goes Wrong

- **"Module not found"** → Install that specific module: `py -m pip install module_name`
- **"CUDA error"** → That's normal, it will use CPU instead
- **Long processing time** → Normal for first run (downloads models)

## 📋 What Each Package Does

- **Flask** - Web framework for API
- **torch/torchvision** - PyTorch for AI models  
- **transformers** - Hugging Face models (ResNet, DistilBERT)
- **Pillow** - Image processing
- **numpy** - Numerical computing

## ⚡ Quick Start

Once installed, just run:
```powershell
py app.py
```

Then visit: http://localhost:5000/health



