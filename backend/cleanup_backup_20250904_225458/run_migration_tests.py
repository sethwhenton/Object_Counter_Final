#!/usr/bin/python3
"""Run Migration Tests with Cleanup"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"SUCCESS: {description} completed successfully")
            return True
        else:
            print(f"ERROR: {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to run {script_name}: {e}")
        return False

def main():
    """Main test runner"""
    print("ObjectType Migration Test Suite")
    print("=" * 60)
    
    # Step 1: Clean up any existing test data
    if not run_script("cleanup_test_data.py", "Cleanup Test Data"):
        print("WARNING: Cleanup failed, but continuing with tests...")
    
    # Step 2: Test engine fixes
    if not run_script("test_engine_fixes.py", "Test Engine Fixes"):
        print("ERROR: Engine fixes test failed")
        return False
    
    # Step 3: Run ObjectType migration test
    if not run_script("test_object_type_migration.py", "ObjectType Migration Test"):
        print("ERROR: ObjectType migration test failed")
        return False
    
    # Step 4: Create default object types
    if not run_script("migrate_object_types.py", "Create Default Object Types"):
        print("ERROR: Default object types creation failed")
        return False
    
    print("\n" + "="*60)
    print("SUCCESS: All ObjectType migration tests passed!")
    print("Phase 3.1: ObjectType Model Migration - COMPLETE!")
    print("Ready to proceed to Step 3.2: Migrate Input Model")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
