#!/usr/bin/env python3
"""
Fix image paths for proper web serving
Handle Windows path separators and ensure correct format for web URLs
"""

import os
from app import app
from models.database import db, Input

def fix_image_paths():
    """Fix image paths to work with web URLs"""
    print("🔧 Fixing image paths for web serving...")
    print("=" * 50)
    
    with app.app_context():
        try:
            inputs = Input.query.all()
            print(f"📋 Found {len(inputs)} input records")
            
            fixed_count = 0
            for input_record in inputs:
                old_path = input_record.image_path
                
                if old_path:
                    # Remove 'uploads\' or 'uploads/' prefix and normalize separators
                    if old_path.startswith('uploads\\') or old_path.startswith('uploads/'):
                        # Extract just the filename
                        filename = os.path.basename(old_path)
                        input_record.image_path = filename
                        fixed_count += 1
                        print(f"   ✅ Fixed: {old_path} → {filename}")
                    else:
                        # If it doesn't start with uploads, assume it's already just a filename
                        filename = os.path.basename(old_path)
                        if filename != old_path:
                            input_record.image_path = filename
                            fixed_count += 1
                            print(f"   ✅ Normalized: {old_path} → {filename}")
                        else:
                            print(f"   ℹ️  Already correct: {old_path}")
            
            if fixed_count > 0:
                db.session.commit()
                print(f"\n✅ Fixed {fixed_count} image paths")
            else:
                print(f"\n✅ All paths already correct")
                
            # Verify the fix
            print(f"\n📊 Current database paths:")
            for input_record in Input.query.all():
                filename = input_record.image_path
                file_path = os.path.join('uploads', filename) if filename else None
                exists = os.path.exists(file_path) if file_path else False
                status = "✅" if exists else "❌"
                print(f"   {status} ID {input_record.id}: {filename}")
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            db.session.rollback()
            raise e

if __name__ == "__main__":
    print("🚀 Image Path Fixer")
    print("=" * 50)
    
    fix_image_paths()
    
    print(f"\n🎉 Path fix complete!")
    print(f"📱 Test image loading at: http://127.0.0.1:5000/uploads/<filename>")
