#!/usr/bin/env python3
"""
Database initialization script
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app
from models.database import db, ObjectType

def init_database():
    """Initialize the database and create tables"""
    print("🗄️ Initializing Database...")
    print("=" * 40)
    
    with app.app_context():
        try:
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Check if object types exist
            existing_types = ObjectType.query.all()
            if existing_types:
                print(f"✅ Found {len(existing_types)} existing object types:")
                for obj_type in existing_types:
                    print(f"   - {obj_type.name}: {obj_type.description}")
            else:
                print("📦 Initializing object types...")
                
                object_types_data = [
                    {'name': 'person', 'description': 'People and humans'},
                    {'name': 'car', 'description': 'Automobiles and vehicles'},
                    {'name': 'bus', 'description': 'Buses and public transport vehicles'},
                    {'name': 'bicycle', 'description': 'Bicycles and bikes'},
                    {'name': 'motorcycle', 'description': 'Motorcycles and motorbikes'},
                    {'name': 'dog', 'description': 'Dogs and canines'},
                    {'name': 'cat', 'description': 'Domestic cats'},
                    {'name': 'bird', 'description': 'Birds and flying animals'},
                    {'name': 'tree', 'description': 'Trees and large plants'},
                    {'name': 'building', 'description': 'Buildings and structures'},
                    {'name': 'road', 'description': 'Roads and pathways'},
                    {'name': 'sky', 'description': 'Sky and atmospheric elements'}
                ]
                
                for obj_data in object_types_data:
                    obj_type = ObjectType(name=obj_data['name'], description=obj_data['description'])
                    db.session.add(obj_type)
                
                db.session.commit()
                print(f"✅ Created {len(object_types_data)} object types!")
                
                for obj_data in object_types_data:
                    print(f"   - {obj_data['name']}: {obj_data['description']}")
            
            print()
            print("🎉 Database initialization complete!")
            print()
            print("📋 Database Schema:")
            print("   📊 object_types - Available object categories")
            print("   📁 inputs - Uploaded images and metadata")
            print("   📈 outputs - Predictions and corrections")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise e

if __name__ == "__main__":
    init_database()



