#!/usr/bin/python3
"""Input Model - Module"""
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import String, Column, Text
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import relationship
from typing import Optional, List, Dict, Any, Union
from .base_model import Base, BaseModel

class Input(BaseModel, Base):
    """Creating an Input table in the database
    Args
        description: Description prompt to give to the model
        image_path: Path to the submitted image
    """
    __tablename__ = 'inputs'
    description = Column(Text, nullable=False)
    image_path = Column(String(200), nullable=False, unique=True)
    outputs = relationship("Output", back_populates="input", cascade="all, delete-orphan")

    def __init__(self) -> None:
        """initializes Input class"""
        super().__init__()

