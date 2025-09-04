#!/usr/bin/python3
"""Start MySQL manually without Windows service"""

import subprocess
import sys
import os
import time
import signal

# MySQL installation path
MYSQL_PATH = r"C:\Users\whent\OneDrive\Documents\AI_lab_engineering_proj\mysql-9.4.0-winx64"
MYSQLD_EXE = os.path.join(MYSQL_PATH, "bin", "mysqld.exe")
MYSQL_EXE = os.path.join(MYSQL_PATH, "bin", "mysql.exe")

def start_mysql_manually():
    """Start MySQL server manually"""
    try:
        print("🚀 Starting MySQL server manually...")
        print(f"🔧 Using: {MYSQLD_EXE}")
        
        # Start MySQL server in background
        process = subprocess.Popen(
            [MYSQLD_EXE, "--console"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ MySQL server started!")
        print("💡 Press Ctrl+C to stop the server")
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping MySQL server...")
            process.terminate()
            process.wait()
            print("✅ MySQL server stopped")
            
    except Exception as e:
        print(f"❌ Error starting MySQL: {e}")
        return False
    
    return True

def test_mysql_connection():
    """Test MySQL connection"""
    try:
        print("🧪 Testing MySQL connection...")
        result = subprocess.run(
            f'"{MYSQL_EXE}" --version',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ MySQL connection test successful: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ MySQL connection test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MySQL connection: {e}")
        return False

def main():
    """Main function"""
    print("🔧 MySQL Manual Starter")
    print("=" * 30)
    
    # Check if MySQL executables exist
    if not os.path.exists(MYSQLD_EXE):
        print(f"❌ MySQL server not found at: {MYSQLD_EXE}")
        sys.exit(1)
    
    if not os.path.exists(MYSQL_EXE):
        print(f"❌ MySQL client not found at: {MYSQL_EXE}")
        sys.exit(1)
    
    print("✅ MySQL executables found")
    
    # Test connection first
    if test_mysql_connection():
        print("✅ MySQL is already running!")
        return
    
    # Start MySQL manually
    start_mysql_manually()

if __name__ == "__main__":
    main()
