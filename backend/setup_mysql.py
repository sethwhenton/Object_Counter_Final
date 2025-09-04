#!/usr/bin/env python3
"""
MySQL Database Setup Script
"""

import os
import mysql.connector
from mysql.connector import Error

def create_mysql_database():
    """Create MySQL database if it doesn't exist"""
    print("🐬 Setting up MySQL Database...")
    print("=" * 40)
    
    # MySQL connection parameters
    host = os.environ.get('MYSQL_HOST', 'localhost')
    port = os.environ.get('MYSQL_PORT', '3306')
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'object_counting')
    
    try:
        # Connect to MySQL server (without database)
        print(f"📡 Connecting to MySQL server at {host}:{port}...")
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            print(f"🗄️ Creating database '{database}' if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            
            print(f"✅ Database '{database}' is ready!")
            
            # Show existing databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"\n📋 Available databases:")
            for db in databases:
                marker = "👉" if db[0] == database else "  "
                print(f"   {marker} {db[0]}")
            
            cursor.close()
            connection.close()
            
            print(f"\n🎉 MySQL setup complete!")
            print(f"🔗 Connection string: mysql+pymysql://{user}:****@{host}:{port}/{database}")
            
            return True
            
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print(f"\n💡 Make sure:")
        print(f"   1. MySQL server is running")
        print(f"   2. Credentials are correct")
        print(f"   3. User has CREATE DATABASE permissions")
        return False

def test_mysql_connection():
    """Test MySQL connection with the app configuration"""
    print("\n🧪 Testing MySQL Connection with Flask App...")
    
    # Set environment to use MySQL
    os.environ['DATABASE_TYPE'] = 'mysql'
    
    try:
        from app import app
        from models.database import db
        
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ Flask + MySQL connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Flask + MySQL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MySQL Database Setup")
    print("=" * 50)
    
    # Check if MySQL credentials are set
    if not os.environ.get('MYSQL_PASSWORD'):
        print("⚠️  MySQL password not set. Using empty password.")
        print("   Set MYSQL_PASSWORD environment variable if needed.")
        print()
    
    # Create database
    if create_mysql_database():
        # Test connection
        test_mysql_connection()
    else:
        print("\n📝 To use MySQL, set these environment variables:")
        print("   $env:DATABASE_TYPE='mysql'")
        print("   $env:MYSQL_HOST='localhost'")
        print("   $env:MYSQL_USER='root'")
        print("   $env:MYSQL_PASSWORD='your_password'")
        print("   $env:MYSQL_DATABASE='object_counting'")
        print("\n🔄 For now, continuing with SQLite...")




