#!/usr/bin/python3
"""Object_type Model - Module"""
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import String, Column, Text
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import relationship
from typing import Optional, List, Dict, Any, Union
from .base_model import Base, BaseModel

class ObjectType(BaseModel, Base):
    """Creating an Object_type table in the database
    Args
        name: name of the object type
        description: A simple description of the object
    """
    __tablename__ = 'object_types'
    name = Column(String(128), nullable=False, unique=True)
    description = Column(String(128), nullable=False)
    outputs = relationship("Output", back_populates="object_type", cascade="all, delete-orphan")

    def __init__(self) -> None:
        """initializes Object_type class"""
        super().__init__()

