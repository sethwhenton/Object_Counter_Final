
from datetime import timedelta
from typing import Optional, List, Dict, Any, Union
from typing import Optional, List, Dict, Any, Union
import os
class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL Database settings - Primary configuration
    OBJ_DETECT_MYSQL_USER = os.environ.get('OBJ_DETECT_MYSQL_USER', 'obj_detect_dev')
    OBJ_DETECT_MYSQL_PWD = os.environ.get('OBJ_DETECT_MYSQL_PWD', 'obj_detect_dev_pwd')
    OBJ_DETECT_MYSQL_HOST = os.environ.get('OBJ_DETECT_MYSQL_HOST', 'localhost')
    OBJ_DETECT_MYSQL_DB = os.environ.get('OBJ_DETECT_MYSQL_DB', 'obj_detect_dev_db')
    OBJ_DETECT_ENV = os.environ.get('OBJ_DETECT_ENV', 'development')
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    
    # API settings
    API_TITLE = 'Object Counting API'
    API_VERSION = 'v1'
    
    @staticmethod
    def init_app(app) -> None:
        """Initialize app with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    OBJ_DETECT_ENV = 'test'
    OBJ_DETECT_MYSQL_USER = os.environ.get('OBJ_DETECT_MYSQL_USER', 'obj_detect_test')
    OBJ_DETECT_MYSQL_PWD = os.environ.get('OBJ_DETECT_MYSQL_PWD', 'obj_detect_test_pwd')
    OBJ_DETECT_MYSQL_HOST = os.environ.get('OBJ_DETECT_MYSQL_HOST', 'localhost')
    OBJ_DETECT_MYSQL_DB = os.environ.get('OBJ_DETECT_MYSQL_DB', 'obj_detect_test_db')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def allowed_file(filename) -> None:
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS