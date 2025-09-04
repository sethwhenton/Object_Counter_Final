#!/usr/bin/python3
"""Install MySQL as a Windows service"""

import subprocess
import sys
import os

# MySQL installation path
MYSQL_PATH = r"C:\Users\whent\OneDrive\Documents\AI_lab_engineering_proj\mysql-9.4.0-winx64"
MYSQLD_EXE = os.path.join(MYSQL_PATH, "bin", "mysqld.exe")

def install_mysql_service():
    """Install MySQL as a Windows service"""
    try:
        print("Installing MySQL as Windows service...")
        print(f"Using: {MYSQLD_EXE}")
        
        # Install MySQL service
        result = subprocess.run(
            f'"{MYSQLD_EXE}" --install',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("SUCCESS: MySQL service installed successfully!")
            return True
        else:
            print(f"ERROR: Failed to install MySQL service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error installing MySQL service: {e}")
        return False

def start_mysql_service():
    """Start MySQL service"""
    try:
        print("Starting MySQL service...")
        
        result = subprocess.run(
            'net start mysql',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("SUCCESS: MySQL service started successfully!")
            return True
        else:
            print(f"ERROR: Failed to start MySQL service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error starting MySQL service: {e}")
        return False

def main():
    """Main function"""
    print("MySQL Service Installer")
    print("=" * 30)
    
    # Check if MySQL server exists
    if not os.path.exists(MYSQLD_EXE):
        print(f"ERROR: MySQL server not found at: {MYSQLD_EXE}")
        sys.exit(1)
    
    print("SUCCESS: MySQL server found")
    
    # Install service
    if install_mysql_service():
        # Start service
        if start_mysql_service():
            print("SUCCESS: MySQL service is now running!")
            print("TIP: You can now run: python setup_mysql.py")
        else:
            print("ERROR: Service installed but failed to start")
            print("TIP: Try running as Administrator")
    else:
        print("ERROR: Failed to install MySQL service")
        print("TIP: Try running as Administrator")

if __name__ == "__main__":
    main()
