#!/usr/bin/env python3
"""
Reset object types in database with new candidate labels
"""

from app import app
from models.database import db, ObjectType

def reset_object_types():
    """Clear existing object types and create new ones"""
    print("🔄 Resetting Object Types...")
    print("=" * 40)
    
    with app.app_context():
        try:
            # Delete all existing object types
            print("🗑️ Removing existing object types...")
            ObjectType.query.delete()
            db.session.commit()
            print("✅ Existing object types removed!")
            
            # Create new object types
            print("📦 Creating new object types...")
            
            new_object_types = [
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
            
            for obj_data in new_object_types:
                obj_type = ObjectType(name=obj_data['name'], description=obj_data['description'])
                db.session.add(obj_type)
            
            db.session.commit()
            print(f"✅ Created {len(new_object_types)} new object types!")
            
            print("\n📋 New Object Types:")
            for i, obj_data in enumerate(new_object_types, 1):
                print(f"   {i:2d}. {obj_data['name']:12} - {obj_data['description']}")
            
            print(f"\n🎉 Object types successfully updated!")
            print(f"📊 Total: {len(new_object_types)} object types")
            
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
            raise e

if __name__ == "__main__":
    reset_object_types()




