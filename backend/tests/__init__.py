#!/usr/bin/python3
"""Tests package for Object Counting API
Comprehensive test suite for the restructured MySQL application
"""
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set up test environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_test_db'  # Use test database
os.environ['OBJ_DETECT_ENV'] = 'test'

# Test configuration
TEST_CONFIG = {
    'database': {
        'user': 'obj_detect_dev',
        'password': 'obj_detect_dev_pwd',
        'host': 'localhost',
        'database': 'obj_detect_test_db'
    },
    'api': {
        'base_url': 'http://localhost:5000',
        'timeout': 30
    },
    'test_data': {
        'sample_image_path': 'test_data/sample_image.jpg',
        'sample_object_types': ['car', 'person', 'dog', 'cat', 'tree']
    }
}


