#!/usr/bin/python3
"""ObjectType Migration Utility"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = os.getenv('OBJ_DETECT_MYSQL_USER', 'obj_detect_dev')
os.environ['OBJ_DETECT_MYSQL_PWD'] = os.getenv('OBJ_DETECT_MYSQL_PWD', 'obj_detect_dev_pwd')
os.environ['OBJ_DETECT_MYSQL_HOST'] = os.getenv('OBJ_DETECT_MYSQL_HOST', 'localhost')
os.environ['OBJ_DETECT_MYSQL_DB'] = os.getenv('OBJ_DETECT_MYSQL_DB', 'obj_detect_dev_db')
os.environ['OBJ_DETECT_ENV'] = os.getenv('OBJ_DETECT_ENV', 'development')

def create_default_object_types():
    """Create default object types for the new system"""
    print("Creating Default Object Types...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        engine = Engine()
        engine.reload()
        
        # Default object types
        default_types = [
            {"name": "person", "description": "Human beings and people"},
            {"name": "car", "description": "Automobiles and vehicles"},
            {"name": "bicycle", "description": "Bicycles and bikes"},
            {"name": "dog", "description": "Dogs and canines"},
            {"name": "cat", "description": "Cats and felines"},
            {"name": "chair", "description": "Chairs and seating furniture"},
            {"name": "bottle", "description": "Bottles and containers"},
            {"name": "cup", "description": "Cups and mugs"},
            {"name": "laptop", "description": "Laptops and computers"},
            {"name": "book", "description": "Books and reading materials"}
        ]
        
        created_count = 0
        for type_data in default_types:
            # Check if object type already exists
            existing = engine.get_by_name(ObjectType, name=type_data["name"])
            if not existing:
                obj_type = ObjectType()
                obj_type.name = type_data["name"]
                obj_type.description = type_data["description"]
                
                engine.new(obj_type)
                created_count += 1
                print(f"Created: {obj_type.name} - {obj_type.id}")
            else:
                print(f"Already exists: {type_data['name']}")
        
        if created_count > 0:
            engine.save()
            print(f"\nSUCCESS: Created {created_count} new object types")
        else:
            print("\nINFO: All default object types already exist")
        
        # Show all object types
        all_types = engine.get_all(ObjectType)
        print(f"\nTotal object types in database: {len(all_types)}")
        for obj_type in all_types:
            print(f"  - {obj_type.name}: {obj_type.id}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create default object types: {e}")
        return False

def verify_object_types():
    """Verify object types are working correctly"""
    print("\nVerifying Object Types...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        engine = Engine()
        
        # Test basic operations
        all_types = engine.get_all(ObjectType)
        print(f"Found {len(all_types)} object types")
        
        if all_types:
            # Test getting by ID
            first_type = all_types[0]
            retrieved = engine.get(ObjectType, id=first_type.id)
            if retrieved:
                print(f"SUCCESS: Retrieved by ID: {retrieved.name}")
            else:
                print("ERROR: Failed to retrieve by ID")
                return False
            
            # Test getting by name
            retrieved_by_name = engine.get_by_name(ObjectType, name=first_type.name)
            if retrieved_by_name:
                print(f"SUCCESS: Retrieved by name: {retrieved_by_name.name}")
            else:
                print("ERROR: Failed to retrieve by name")
                return False
        
        print("SUCCESS: Object types verification passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Object types verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("ObjectType Migration Utility")
    print("=" * 50)
    
    # Create default object types
    if not create_default_object_types():
        print("ERROR: Failed to create default object types")
        return False
    
    # Verify everything is working
    if not verify_object_types():
        print("ERROR: Object types verification failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS: ObjectType migration completed!")
    print("Ready to proceed to Input model migration")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
