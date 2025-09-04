#!/usr/bin/env python3
"""
Migration script to fix image paths in database
Converts full paths like 'uploads/filename.jpg' to just 'filename.jpg'
"""

import os
from app import app
from models.database import db, ObjectType, Input, Output

def migrate_image_paths():
    """Update image paths in database to store just filenames"""
    print("🔄 Migrating image paths in database...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get all input records
            inputs = Input.query.all()
            print(f"📋 Found {len(inputs)} input records to check")
            
            updated_count = 0
            for input_record in inputs:
                old_path = input_record.image_path
                
                # Check if path starts with 'uploads/'
                if old_path and old_path.startswith('uploads/'):
                    # Extract just the filename
                    new_path = old_path.replace('uploads/', '')
                    input_record.image_path = new_path
                    updated_count += 1
                    print(f"   ✅ Updated: {old_path} → {new_path}")
                elif old_path:
                    print(f"   ℹ️  Skipped: {old_path} (already correct format)")
                else:
                    print(f"   ⚠️  Warning: Empty image path for input ID {input_record.id}")
            
            if updated_count > 0:
                db.session.commit()
                print(f"\n✅ Migration complete! Updated {updated_count} records")
            else:
                print(f"\n✅ No migration needed - all paths already in correct format")
                
            # Verify migration
            print(f"\n📊 Verification:")
            for input_record in Input.query.all():
                print(f"   ID {input_record.id}: {input_record.image_path}")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise e

def verify_file_existence():
    """Check if image files exist on disk"""
    print("\n🔍 Verifying file existence...")
    print("=" * 50)
    
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        print(f"⚠️  Upload folder '{upload_folder}' does not exist")
        return
        
    with app.app_context():
        inputs = Input.query.all()
        existing_count = 0
        missing_count = 0
        
        for input_record in inputs:
            if input_record.image_path:
                file_path = os.path.join(upload_folder, input_record.image_path)
                if os.path.exists(file_path):
                    existing_count += 1
                    print(f"   ✅ Exists: {input_record.image_path}")
                else:
                    missing_count += 1
                    print(f"   ❌ Missing: {input_record.image_path}")
        
        print(f"\n📊 File existence summary:")
        print(f"   ✅ Existing files: {existing_count}")
        print(f"   ❌ Missing files: {missing_count}")
        print(f"   📁 Total records: {len(inputs)}")

if __name__ == "__main__":
    print("🚀 Image Path Migration Tool")
    print("=" * 50)
    
    migrate_image_paths()
    verify_file_existence()
    
    print(f"\n🎉 Migration complete!")
    print(f"📱 Images should now load in the frontend at:")
    print(f"   http://127.0.0.1:5000/uploads/<filename>")
