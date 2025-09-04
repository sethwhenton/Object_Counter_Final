#!/usr/bin/env python3
"""
Setup script for the Object Counting Backend
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def setup_backend():
    """Setup the backend environment"""
    print("🚀 Setting up Object Counting Backend")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        if not run_command("py -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    if not run_command(activate_cmd, "Installing Python dependencies"):
        print("⚠️  Dependency installation failed. You may need to install manually:")
        print("   1. Activate virtual environment:")
        if os.name == 'nt':
            print("      venv\\Scripts\\activate")
        else:
            print("      source venv/bin/activate")
        print("   2. Install requirements:")
        print("      pip install -r requirements.txt")
        return False
    
    # Install PyTorch with CPU support (for compatibility)
    pytorch_cmd = "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
    if os.name == 'nt':
        pytorch_cmd = f"venv\\Scripts\\activate && {pytorch_cmd}"
    else:
        pytorch_cmd = f"source venv/bin/activate && {pytorch_cmd}"
    
    run_command(pytorch_cmd, "Installing PyTorch (CPU version)")
    
    # Install Segment Anything
    sam_cmd = "pip install git+https://github.com/facebookresearch/segment-anything.git"
    if os.name == 'nt':
        sam_cmd = f"venv\\Scripts\\activate && {sam_cmd}"
    else:
        sam_cmd = f"source venv/bin/activate && {sam_cmd}"
    
    run_command(sam_cmd, "Installing Segment Anything Model")
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    print("✅ Created uploads directory")
    
    print("\n" + "=" * 50)
    print("🎉 Backend setup complete!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the Flask app:")
    print("   python app.py")
    print("3. Test the API:")
    print("   python test_pipeline.py")
    
    return True

if __name__ == "__main__":
    setup_backend()
