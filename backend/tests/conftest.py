#!/usr/bin/python3
"""Test Configuration and Fixtures
Pytest configuration and shared test fixtures
"""
import os
import sys
import pytest
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import TEST_CONFIG


@pytest.fixture(scope="session")
def test_app():
    """Create test Flask app"""
    import app_restructured
    app = app_restructured.app
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def test_client(test_app):
    """Create test client"""
    return test_app.test_client()


@pytest.fixture(scope="session")
def test_database():
    """Set up test database"""
    from storage import database
    from storage.database_functions import init_database
    
    database.reload()
    init_database()
    
    yield database
    
    # Cleanup after tests
    cleanup_test_database()


@pytest.fixture
def sample_object_type(test_database):
    """Create a sample object type for testing"""
    from storage.object_types import ObjectType
    
    obj_type = ObjectType()
    obj_type.name = f"test_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    obj_type.description = "Sample object type for testing"
    
    test_database.new(obj_type)
    test_database.save()
    
    yield obj_type
    
    # Cleanup
    try:
        test_database.delete(obj_type)
    except:
        pass


@pytest.fixture
def sample_input(test_database):
    """Create a sample input for testing"""
    from storage.inputs import Input
    
    input_record = Input()
    input_record.image_path = f"test_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    input_record.description = "Sample input for testing"
    
    test_database.new(input_record)
    test_database.save()
    
    yield input_record
    
    # Cleanup
    try:
        test_database.delete(input_record)
    except:
        pass


@pytest.fixture
def sample_output(test_database, sample_object_type, sample_input):
    """Create a sample output for testing"""
    from storage.outputs import Output
    
    output = Output()
    output.predicted_count = 5
    output.pred_confidence = 0.85
    output.object_type_id = sample_object_type.id
    output.input_id = sample_input.id
    
    test_database.new(output)
    test_database.save()
    
    yield output
    
    # Cleanup
    try:
        test_database.delete(output)
    except:
        pass


def cleanup_test_database():
    """Clean up test database"""
    try:
        from storage.database_functions import get_all_outputs, delete_output
        from storage import database
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Clean up test outputs
        outputs = get_all_outputs()
        test_outputs = [output for output in outputs if 'test_' in str(output.id)]
        
        for output in test_outputs:
            try:
                delete_output(output.id)
            except:
                pass
        
        # Clean up test object types
        object_types = database.get_all(ObjectType)
        test_types = [obj_type for obj_type in object_types if 'test_' in obj_type.name]
        
        for obj_type in test_types:
            try:
                database.delete(obj_type)
            except:
                pass
        
        # Clean up test inputs
        inputs = database.get_all(Input)
        test_inputs = [input_record for input_record in inputs if 'test_' in input_record.image_path]
        
        for input_record in test_inputs:
            try:
                database.delete(input_record)
            except:
                pass
        
    except Exception as e:
        print(f"Warning: Failed to cleanup test database: {e}")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Mark slow tests
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.nodeid or "test_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests
        if "test_storage" in item.nodeid:
            item.add_marker(pytest.mark.unit)


