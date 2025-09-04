#!/usr/bin/python3
"""create a unique Storage instance for the application"""
from .engine.engine import Engine
from .base_model import BaseModel
from .inputs import Input
from .object_types import ObjectType
from .outputs import Output
from os import getenv


# Initialize database engine
database = Engine()
database.reload()

# Import models after engine is initialized to avoid circular imports
from .base_model import Base
from .inputs import Input
from .object_types import ObjectType
from .outputs import Output