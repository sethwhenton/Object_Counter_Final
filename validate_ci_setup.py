#!/usr/bin/python3
"""CI/CD Setup Validation Script
Validates that all CI/CD components are properly configured
"""
import os
import sys
import yaml
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def validate_gitlab_ci():
    """Validate GitLab CI configuration"""
    print("🔍 Validating GitLab CI configuration...")
    
    if not check_file_exists('.gitlab-ci.yml', 'GitLab CI configuration'):
        return False
    
    try:
        with open('.gitlab-ci.yml', 'r') as f:
            ci_config = yaml.safe_load(f)
        
        # Check required stages
        required_stages = ['test', 'build', 'deploy']
        stages = ci_config.get('stages', [])
        
        for stage in required_stages:
            if stage in stages:
                print(f"✅ Stage '{stage}' configured")
            else:
                print(f"❌ Stage '{stage}' missing")
                return False
        
        # Check test jobs
        test_jobs = ['test', 'test_api', 'test_storage']
        for job in test_jobs:
            if job in ci_config:
                print(f"✅ Test job '{job}' configured")
            else:
                print(f"❌ Test job '{job}' missing")
                return False
        
        print("✅ GitLab CI configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ GitLab CI configuration error: {e}")
        return False

def validate_test_infrastructure():
    """Validate test infrastructure"""
    print("🔍 Validating test infrastructure...")
    
    required_files = [
        ('backend/tests/test_runner.py', 'Test runner'),
        ('backend/tests/ci_test_runner.py', 'CI test runner'),
        ('backend/tests/conftest.py', 'Test configuration'),
        ('backend/tests/test_api/test_inputs.py', 'API input tests'),
        ('backend/tests/test_api/test_outputs.py', 'API output tests'),
        ('backend/tests/test_api/test_object_types.py', 'API object type tests'),
        ('backend/tests/test_storage/test_database.py', 'Storage tests'),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def validate_database_setup():
    """Validate database setup scripts"""
    print("🔍 Validating database setup...")
    
    required_files = [
        ('backend/setup_ci_database.py', 'CI database setup'),
        ('backend/storage/database_functions.py', 'Database functions'),
        ('backend/storage/engine/engine.py', 'Database engine'),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def validate_requirements():
    """Validate requirements files"""
    print("🔍 Validating requirements files...")
    
    required_files = [
        ('requirements.txt', 'Main requirements'),
        ('requirements-ci.txt', 'CI requirements'),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def validate_documentation():
    """Validate documentation"""
    print("🔍 Validating documentation...")
    
    required_files = [
        ('CI_CD_SETUP.md', 'CI/CD documentation'),
        ('README.md', 'Main documentation'),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def main():
    """Main validation function"""
    print("🚀 CI/CD Setup Validation")
    print("=" * 50)
    
    validations = [
        ("GitLab CI Configuration", validate_gitlab_ci),
        ("Test Infrastructure", validate_test_infrastructure),
        ("Database Setup", validate_database_setup),
        ("Requirements Files", validate_requirements),
        ("Documentation", validate_documentation),
    ]
    
    all_valid = True
    
    for name, validation_func in validations:
        print(f"\n📋 {name}")
        print("-" * 30)
        if not validation_func():
            all_valid = False
            print(f"❌ {name} validation failed")
        else:
            print(f"✅ {name} validation passed")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All CI/CD components are properly configured!")
        print("✅ Ready for GitLab CI/CD pipeline deployment")
        return 0
    else:
        print("❌ Some CI/CD components are missing or misconfigured")
        print("🔧 Please fix the issues above before deploying")
        return 1

if __name__ == '__main__':
    sys.exit(main())


