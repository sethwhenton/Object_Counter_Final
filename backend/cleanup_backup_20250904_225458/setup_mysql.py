#!/usr/bin/python3
"""Setup MySQL database for the application"""

import subprocess
import sys
import os
import time
from mysql_service_manager import MySQLServiceManager

def run_sql_script(script_path, user='root', password=''):
    """Run a SQL script using mysql command"""
    try:
        if password:
            cmd = f'mysql -u {user} -p{password} < {script_path}'
        else:
            cmd = f'mysql -u {user} < {script_path}'
        
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"SUCCESS: Successfully executed {script_path}")
            return True
        else:
            print(f"ERROR: Error executing {script_path}:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Exception running {script_path}: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up MySQL database for Object Counting System")
    print("=" * 60)
    
    # Initialize service manager
    service_manager = MySQLServiceManager()
    
    # Check MySQL service status
    print("Checking MySQL service status...")
    is_running, service_name = service_manager.check_service_status()
    
    if not is_running:
        if service_name:
            print(f"WARNING: MySQL service is not running. Attempting to start...")
            if not service_manager.start_service(service_name):
                print("ERROR: Failed to start MySQL service")
                print("TIP: You may need to run as Administrator")
                print("TIP: Try running: net start mysql")
                sys.exit(1)
            time.sleep(3)  # Wait for service to start
        else:
            print("ERROR: No MySQL service found")
            print("TIP: Please install MySQL or check if it's running")
            print("TIP: Common service names: MySQL, MySQL80, MySQL90, MySQL94")
            sys.exit(1)
    
    # Check if MySQL is available in PATH
    try:
        result = subprocess.run("mysql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCCESS: MySQL found: {result.stdout.strip()}")
        else:
            print("ERROR: MySQL not found in PATH")
            print("TIP: Please add MySQL to your PATH or restart Command Prompt")
            print("TIP: MySQL should be in: C:\\Users\\whent\\OneDrive\\Documents\\AI_lab_engineering_proj\\mysql-9.4.0-winx64\\bin")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Error checking MySQL: {e}")
        sys.exit(1)
    
    # Get MySQL root password
    print("\nMySQL Setup")
    print("You'll need MySQL root access to create the database and user.")
    root_password = input("Enter MySQL root password (or press Enter if no password): ").strip()
    
    # Create development database
    print("\nCreating development database...")
    if run_sql_script("create_db.sql", password=root_password):
        print("SUCCESS: Development database created successfully")
    else:
        print("ERROR: Failed to create development database")
        sys.exit(1)
    
    # Create test database
    print("\nCreating test database...")
    if run_sql_script("create_test_db.sql", password=root_password):
        print("SUCCESS: Test database created successfully")
    else:
        print("ERROR: Failed to create test database")
        sys.exit(1)
    
    print("\nSUCCESS: MySQL setup completed successfully!")
    print("\nNext steps:")
    print("1. Test the connection: python test_mysql_connection_fixed.py")
    print("2. Start the application: python app.py")

if __name__ == "__main__":
    main()