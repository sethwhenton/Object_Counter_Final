#!/usr/bin/python3
"""Complete Development Environment Setup Script"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"STEP: {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCCESS: {description} completed successfully")
            return True
        else:
            print(f"ERROR: {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Error during {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"SUCCESS: Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"ERROR: Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("TIP: Please use Python 3.8 or higher")
        return False

def setup_virtual_environment():
    """Set up virtual environment"""
    venv_path = "backend/venv"
    
    if os.path.exists(venv_path):
        print("SUCCESS: Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    if run_command(f"python -m venv {venv_path}", "Creating virtual environment"):
        print("SUCCESS: Virtual environment created successfully")
        return True
    else:
        print("ERROR: Failed to create virtual environment")
        return False

def activate_and_install_dependencies():
    """Activate virtual environment and install dependencies"""
    if platform.system() == "Windows":
        activate_script = "backend/venv/Scripts/activate"
        pip_command = "backend/venv/Scripts/pip"
    else:
        activate_script = "backend/venv/bin/activate"
        pip_command = "backend/venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f'"{pip_command}" install --upgrade pip', "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f'"{pip_command}" install -r requirements.txt', "Installing Python dependencies"):
        return False
    
    return True

def setup_mysql_database():
    """Set up MySQL database"""
    print("Setting up MySQL database...")
    
    # Check if MySQL service is running
    if not run_command("python backend/check_mysql_service.py", "Checking MySQL service"):
        print("WARNING: MySQL service not running, attempting to start...")
        if not run_command("python backend/install_mysql_service.py", "Installing MySQL service"):
            print("ERROR: Failed to set up MySQL service")
            return False
    
    # Create databases
    if not run_command("python backend/setup_mysql.py", "Creating MySQL databases"):
        print("ERROR: Failed to create MySQL databases")
        return False
    
    return True

def test_setup():
    """Test the complete setup"""
    print("Testing the setup...")
    
    # Test MySQL connection
    if not run_command("python backend/test_mysql_connection_fixed.py", "Testing MySQL connection"):
        print("ERROR: MySQL connection test failed")
        return False
    
    print("SUCCESS: All tests passed!")
    return True

def main():
    """Main setup function"""
    print("AI Object Counting System - Development Environment Setup")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not activate_and_install_dependencies():
        sys.exit(1)
    
    # Set up MySQL database
    if not setup_mysql_database():
        print("WARNING: MySQL setup failed, but you can continue with development")
        print("TIP: Run 'python backend/setup_mysql.py' manually later")
    
    # Test setup
    if not test_setup():
        print("WARNING: Some tests failed, but basic setup is complete")
    
    print("\nSUCCESS: Development environment setup completed!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if platform.system() == "Windows":
        print("   backend\\venv\\Scripts\\activate")
    else:
        print("   source backend/venv/bin/activate")
    print("2. Start the backend: python backend/app.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("\nTIP: For MySQL issues, run: python backend/setup_mysql.py")

if __name__ == "__main__":
    main()
