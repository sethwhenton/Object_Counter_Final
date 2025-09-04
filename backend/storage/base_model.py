#!/usr/bin/python3
"""Base Model - Module
Description:
    It holds common (a union of) characteristics for other models
    Its herited by other model classes in this project
"""
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import String, Column, DateTime


Base = declarative_base()


class BaseModel:
    """Holds common model attrs and functions for this project
    Attrs:
        id: ID of the row in the database
        created_at: the time the row was created
        updated_at: When the row was last edited
    """
    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self) -> None:
        """Intializes the class
        Return: None
        """
        self.id = str(uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self) -> None:
        """
        Description:
            Update the updated_at field with current date
            and save to database
        """
        # Import here to avoid circular imports
        from . import database
        self.updated_at = datetime.now()
        database.new(self)
        database.save()

    def delete(self) -> None:
        """delete the current instance from the storage"""
        from . import database
        database.delete(self)

    def __str__(self) -> str:
        """Return string representation of the object"""
        self_dict = self.__dict__
        rep = "[{}] ({}) {}".format(self.__class__.__name__,
                                    self.id, self_dict)
        return (rep)