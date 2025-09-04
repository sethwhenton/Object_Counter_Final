#!/usr/bin/python3
"""Cleanup Old Database Code
Remove Flask-SQLAlchemy imports and old database models
"""
import os
import shutil
from datetime import datetime

def backup_old_files():
    """Create backup of old files before deletion"""
    backup_dir = f"backup_old_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "models/database.py",
        "app.py"
    ]
    
    print(f"Creating backup in {backup_dir}/")
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_dir)
            print(f"  ✅ Backed up {file_path}")
        else:
            print(f"  ⚠️  File not found: {file_path}")
    
    return backup_dir

def remove_old_database_files():
    """Remove old database files"""
    files_to_remove = [
        "models/database.py",  # Old Flask-SQLAlchemy database
    ]
    
    print("\nRemoving old database files:")
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  ✅ Removed {file_path}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

def update_imports_in_files():
    """Update imports in files that reference old database code"""
    print("\nUpdating imports in files:")
    
    # Files that might have old imports
    files_to_check = [
        "app.py",
        "test_app.py",
        "test_api_endpoints.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  📝 Checking {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for old imports
                old_imports = [
                    "from models.database import",
                    "from models.database import db",
                    "from models.database import init_database",
                    "from models.database import save_prediction_result",
                    "from models.database import update_correction",
                    "from models.database import get_object_type_by_name",
                    "from models.database import ObjectType",
                    "from models.database import Output",
                    "from models.database import Input"
                ]
                
                has_old_imports = any(old_import in content for old_import in old_imports)
                
                if has_old_imports:
                    print(f"    ⚠️  {file_path} contains old database imports")
                    print(f"    💡 Consider updating to use new MySQL functions")
                else:
                    print(f"    ✅ {file_path} is clean")
                    
            except Exception as e:
                print(f"    ❌ Error reading {file_path}: {e}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

def create_migration_summary():
    """Create a summary of the migration"""
    summary = """
# Database Migration Summary

## Files Removed:
- `models/database.py` - Old Flask-SQLAlchemy database implementation

## Files Created:
- `storage/database_functions.py` - New MySQL database functions
- `storage/object_types.py` - New ObjectType model with UUID
- `storage/inputs.py` - New Input model with UUID  
- `storage/outputs.py` - New Output model with UUID + confidence
- `storage/engine/engine.py` - Custom MySQL engine
- `storage/base_model.py` - Base model with UUID support
- `app_mysql.py` - New Flask app with MySQL
- `app_restructured.py` - Restructured app with Flask-RESTful + Swagger

## Key Changes:
1. **Primary Keys**: Changed from Integer to UUID
2. **Database Engine**: Custom MySQL engine instead of Flask-SQLAlchemy
3. **Confidence Field**: Added pred_confidence to Output model
4. **API Structure**: Flask-RESTful with Swagger documentation
5. **Error Handling**: Improved transaction management with rollback

## Migration Status:
- ✅ Models migrated to UUID
- ✅ Database functions migrated
- ✅ Flask app restructured
- ✅ API documentation added
- ✅ Old code cleaned up

## Next Steps:
1. Test the new restructured app
2. Update frontend if needed for UUID handling
3. Deploy to production
"""
    
    with open("MIGRATION_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n✅ Created MIGRATION_SUMMARY.md")

def main():
    """Main cleanup function"""
    print("Database Code Cleanup")
    print("=" * 30)
    
    # Create backup
    backup_dir = backup_old_files()
    
    # Remove old files
    remove_old_database_files()
    
    # Update imports
    update_imports_in_files()
    
    # Create summary
    create_migration_summary()
    
    print(f"\n🎉 Cleanup complete!")
    print(f"📁 Backup created in: {backup_dir}/")
    print(f"📄 Migration summary: MIGRATION_SUMMARY.md")
    print(f"\nNext steps:")
    print(f"1. Test the restructured app: python app_restructured.py")
    print(f"2. Visit http://localhost:5000/docs for API documentation")
    print(f"3. Update any remaining imports if needed")

if __name__ == "__main__":
    main()
