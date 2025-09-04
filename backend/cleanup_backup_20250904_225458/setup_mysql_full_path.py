#!/usr/bin/python3
"""Setup MySQL database for the application - Full Path Version"""

import subprocess
import sys
import os
import time
from mysql_service_manager import MySQLServiceManager

# MySQL installation path
MYSQL_PATH = r"C:\Users\whent\OneDrive\Documents\AI_lab_engineering_proj\mysql-9.4.0-winx64\bin"
MYSQL_EXE = os.path.join(MYSQL_PATH, "mysql.exe")

def run_sql_script(script_path, user='root', password=''):
    """Run a SQL script using mysql command with full path"""
    try:
        if password:
            cmd = f'"{MYSQL_EXE}" -u {user} -p{password} < {script_path}'
        else:
            cmd = f'"{MYSQL_EXE}" -u {user} < {script_path}'
        
        print(f"🔧 Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully executed {script_path}")
            return True
        else:
            print(f"❌ Error executing {script_path}:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Exception running {script_path}: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up MySQL database for Object Counting System")
    print("=" * 60)
    
    # Initialize service manager
    service_manager = MySQLServiceManager()
    
    # Check MySQL service status
    print("🔍 Checking MySQL service status...")
    is_running, service_name = service_manager.check_service_status()
    
    if not is_running:
        if service_name:
            print(f"⚠️ MySQL service is not running. Attempting to start...")
            if not service_manager.start_service(service_name):
                print("❌ Failed to start MySQL service")
                print("💡 You may need to run as Administrator")
                print("💡 Try running: net start mysql")
                sys.exit(1)
            time.sleep(3)  # Wait for service to start
        else:
            print("❌ No MySQL service found")
            print("💡 Please install MySQL or check if it's running")
            print("💡 Common service names: MySQL, MySQL80, MySQL90, MySQL94")
            sys.exit(1)
    
    # Check if MySQL is available at full path
    try:
        if os.path.exists(MYSQL_EXE):
            result = subprocess.run(f'"{MYSQL_EXE}" --version', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ MySQL found: {result.stdout.strip()}")
            else:
                print(f"❌ MySQL executable found but not working: {MYSQL_EXE}")
                sys.exit(1)
        else:
            print(f"❌ MySQL not found at: {MYSQL_EXE}")
            print("💡 Please check the MySQL installation path")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking MySQL: {e}")
        sys.exit(1)
    
    # Get MySQL root password
    print("\n🔐 MySQL Setup")
    print("You'll need MySQL root access to create the database and user.")
    root_password = input("Enter MySQL root password (or press Enter if no password): ").strip()
    
    # Create development database
    print("\n📦 Creating development database...")
    if run_sql_script("create_db.sql", password=root_password):
        print("✅ Development database created successfully")
    else:
        print("❌ Failed to create development database")
        sys.exit(1)
    
    # Create test database
    print("\n🧪 Creating test database...")
    if run_sql_script("create_test_db.sql", password=root_password):
        print("✅ Test database created successfully")
    else:
        print("❌ Failed to create test database")
        sys.exit(1)
    
    print("\n🎉 MySQL setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the connection: python test_mysql_connection.py")
    print("2. Start the application: python app.py")

if __name__ == "__main__":
    main()
