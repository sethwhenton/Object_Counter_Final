#!/usr/bin/python3
"""Local CI Testing Script
Test CI components locally without requiring GitLab CI environment
"""
import os
import sys
import subprocess
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def test_ci_components():
    """Test CI components locally"""
    print("🧪 Testing CI Components Locally")
    print("=" * 50)
    
    # Set up local environment
    os.environ['OBJ_DETECT_ENV'] = 'test'
    os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
    os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
    os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
    os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_test_db'
    
    tests = [
        ("python tests/test_runner.py --test api", "API Tests"),
        ("python tests/test_runner.py --test storage", "Storage Tests"),
        ("python tests/ci_test_runner.py", "CI Test Runner"),
    ]
    
    all_passed = True
    for command, description in tests:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def validate_ci_files():
    """Validate CI configuration files"""
    print("🔍 Validating CI Configuration Files")
    print("=" * 50)
    
    required_files = [
        '.gitlab-ci.yml',
        'requirements-ci.txt',
        'CI_CD_SETUP.md',
        'backend/setup_ci_database.py',
        'backend/tests/ci_test_runner.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Main function"""
    print("🚀 Local CI Testing")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Validate files
    files_valid = validate_ci_files()
    
    # Test components
    tests_passed = test_ci_components()
    
    print("=" * 50)
    if files_valid and tests_passed:
        print("🎉 All CI components are working correctly!")
        print("✅ Ready for GitLab CI/CD deployment")
        return 0
    else:
        print("❌ Some CI components have issues")
        if not files_valid:
            print("   - Missing configuration files")
        if not tests_passed:
            print("   - Test failures")
        return 1

if __name__ == '__main__':
    sys.exit(main())


