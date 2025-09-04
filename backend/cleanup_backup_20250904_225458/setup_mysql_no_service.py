#!/usr/bin/python3
"""Setup MySQL database without Windows service"""

import subprocess
import sys
import os
import time
import threading

# MySQL installation path
MYSQL_PATH = r"C:\Users\whent\OneDrive\Documents\AI_lab_engineering_proj\mysql-9.4.0-winx64"
MYSQLD_EXE = os.path.join(MYSQL_PATH, "bin", "mysqld.exe")
MYSQL_EXE = os.path.join(MYSQL_PATH, "bin", "mysql.exe")

# Global variable to store MySQL process
mysql_process = None

def start_mysql_server():
    """Start MySQL server in background"""
    global mysql_process
    try:
        print("🚀 Starting MySQL server...")
        print(f"🔧 Using: {MYSQLD_EXE}")
        
        # Start MySQL server in background
        mysql_process = subprocess.Popen(
            [MYSQLD_EXE, "--console"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ MySQL server started!")
        time.sleep(3)  # Wait for server to start
        return True
        
    except Exception as e:
        print(f"❌ Error starting MySQL server: {e}")
        return False

def stop_mysql_server():
    """Stop MySQL server"""
    global mysql_process
    if mysql_process:
        print("🛑 Stopping MySQL server...")
        mysql_process.terminate()
        mysql_process.wait()
        print("✅ MySQL server stopped")

def run_sql_script(script_path, user='root', password=''):
    """Run a SQL script using mysql command"""
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
    
    # Check if MySQL executables exist
    if not os.path.exists(MYSQLD_EXE):
        print(f"❌ MySQL server not found at: {MYSQLD_EXE}")
        sys.exit(1)
    
    if not os.path.exists(MYSQL_EXE):
        print(f"❌ MySQL client not found at: {MYSQL_EXE}")
        sys.exit(1)
    
    print("✅ MySQL executables found")
    
    # Start MySQL server
    if not start_mysql_server():
        print("❌ Failed to start MySQL server")
        sys.exit(1)
    
    try:
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
        print("\n⚠️ Note: MySQL server is running in background")
        print("💡 Press Ctrl+C to stop the server when done")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            stop_mysql_server()
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        stop_mysql_server()
        sys.exit(1)

if __name__ == "__main__":
    main()
