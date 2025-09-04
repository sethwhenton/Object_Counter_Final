from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class ObjectType(db.Model):
    """Model for object types (car, cat, tree, etc.)"""
    __tablename__ = 'object_types'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationship
    outputs = db.relationship('Output', backref='object_type', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'name': self.name,
            'description': self.description
        }

class Input(db.Model):
    """Model for input images"""
    __tablename__ = 'inputs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_path = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Relationship
    outputs = db.relationship('Output', backref='input', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'image_path': self.image_path,
            'description': self.description
        }

class Output(db.Model):
    """Model for prediction outputs and corrections"""
    __tablename__ = 'outputs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    predicted_count = db.Column(db.Integer, nullable=False)
    corrected_count = db.Column(db.Integer, nullable=True)
    object_type_fk = db.Column(db.Integer, db.ForeignKey('object_types.id'), nullable=False)
    input_fk = db.Column(db.Integer, db.ForeignKey('inputs.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'predicted_count': self.predicted_count,
            'corrected_count': self.corrected_count,
            'object_type_id': self.object_type_fk,
            'input_id': self.input_fk,
            'object_type_name': self.object_type.name if self.object_type else None
        }

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize object types if they don't exist
        existing_types = ObjectType.query.all()
        if not existing_types:
            print("📦 Initializing object types...")
            
            object_types = [
                {'name': 'car', 'description': 'Automobiles and vehicles'},
                {'name': 'cat', 'description': 'Domestic cats'},
                {'name': 'tree', 'description': 'Trees and large plants'},
                {'name': 'dog', 'description': 'Dogs and canines'},
                {'name': 'building', 'description': 'Buildings and structures'},
                {'name': 'person', 'description': 'People and humans'},
                {'name': 'sky', 'description': 'Sky and atmospheric elements'},
                {'name': 'ground', 'description': 'Ground and terrain'},
                {'name': 'hardware', 'description': 'Tools and hardware items'}
            ]
            
            for obj_type in object_types:
                new_type = ObjectType(name=obj_type['name'], description=obj_type['description'])
                db.session.add(new_type)
            
            db.session.commit()
            print(f"✅ Created {len(object_types)} object types")
        else:
            print(f"✅ Database already initialized with {len(existing_types)} object types")

def get_object_type_by_name(name):
    """Get object type by name"""
    return ObjectType.query.filter_by(name=name).first()

def save_prediction_result(image_path, object_type_name, predicted_count, description=None):
    """Save a prediction result to database"""
    try:
        # Get or create object type
        object_type = get_object_type_by_name(object_type_name)
        if not object_type:
            raise ValueError(f"Object type '{object_type_name}' not found")
        
        # Create input record
        input_record = Input(image_path=image_path, description=description)
        db.session.add(input_record)
        db.session.flush()  # Get the ID
        
        # Create output record
        output_record = Output(
            predicted_count=predicted_count,
            object_type_fk=object_type.id,
            input_fk=input_record.id
        )
        db.session.add(output_record)
        db.session.commit()
        
        return output_record
        
    except Exception as e:
        db.session.rollback()
        raise e

def update_correction(output_id, corrected_count):
    """Update a prediction with user correction"""
    try:
        output = Output.query.get(output_id)
        if not output:
            raise ValueError(f"Output with ID {output_id} not found")
        
        output.corrected_count = corrected_count
        output.updated_at = datetime.utcnow()
        db.session.commit()
        
        return output
        
    except Exception as e:
        db.session.rollback()
        raise e



