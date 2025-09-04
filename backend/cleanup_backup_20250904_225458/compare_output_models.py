#!/usr/bin/python3
"""Compare Old vs New Output Models"""

def show_old_output_model():
    """Show the old Flask-SQLAlchemy Output model"""
    print("OLD Output Model (Flask-SQLAlchemy):")
    print("=" * 50)
    print("""
class Output(db.Model):
    __tablename__ = 'outputs'
    
    # OLD: Integer primary key
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prediction fields
    predicted_count = db.Column(db.Integer, nullable=False)
    corrected_count = db.Column(db.Integer, nullable=True)
    
    # OLD: Integer foreign keys
    object_type_fk = db.Column(db.Integer, db.ForeignKey('object_types.id'), nullable=False)
    input_fk = db.Column(db.Integer, db.ForeignKey('inputs.id'), nullable=False)
    
    # MISSING: No confidence field
    """)

def show_new_output_model():
    """Show the new custom MySQL Output model"""
    print("NEW Output Model (Custom MySQL Engine):")
    print("=" * 50)
    print("""
class Output(BaseModel, Base):
    __tablename__ = 'outputs'
    
    # NEW: UUID primary key (inherited from BaseModel)
    # id = Column(String(60), primary_key=True, nullable=False)  # From BaseModel
    # created_at = Column(DateTime(), default=datetime.now(), nullable=False)  # From BaseModel
    # updated_at = Column(DateTime(), default=datetime.now(), nullable=False)  # From BaseModel
    
    # Prediction fields
    predicted_count = Column(Integer, nullable=False)
    corrected_count = Column(Integer)
    
    # NEW: Added confidence field
    pred_confidence = Column(Float(), nullable=False)
    
    # NEW: UUID foreign keys
    object_type_id = Column(String(60), ForeignKey("object_types.id"), nullable=False)
    input_id = Column(String(60), ForeignKey("inputs.id"), nullable=False)
    """)

def show_migration_benefits():
    """Show benefits of the Output model migration"""
    print("Output Model Migration Benefits:")
    print("=" * 50)
    print("""
✅ UUID Primary Keys:
   - Globally unique identifiers
   - No collision risk across systems
   - Better for distributed systems
   - More secure (harder to guess)

✅ Added Confidence Field:
   - pred_confidence: Model confidence percentage
   - Better prediction tracking
   - Quality assessment capability
   - Performance monitoring

✅ UUID Foreign Keys:
   - Consistent with primary keys
   - Better relationship integrity
   - Easier to work with across systems
   - More flexible data management

✅ Improved Data Types:
   - Float for confidence (more precise than Integer)
   - Better data representation
   - More accurate confidence tracking

✅ Enhanced Relationships:
   - Better foreign key management
   - Consistent UUID usage
   - Improved data integrity
    """)

def show_field_comparison():
    """Show detailed field comparison"""
    print("Field-by-Field Comparison:")
    print("=" * 50)
    print("""
┌─────────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Field               │ Old Type        │ New Type        │ Status          │
├─────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ id                  │ Integer         │ String(60) UUID │ ✅ MIGRATED     │
│ created_at          │ DateTime        │ DateTime        │ ✅ SAME         │
│ updated_at          │ DateTime        │ DateTime        │ ✅ SAME         │
│ predicted_count     │ Integer         │ Integer         │ ✅ SAME         │
│ corrected_count     │ Integer         │ Integer         │ ✅ SAME         │
│ pred_confidence     │ MISSING         │ Float           │ ✅ ADDED        │
│ object_type_fk      │ Integer FK      │ String(60) FK   │ ✅ MIGRATED     │
│ input_fk            │ Integer FK      │ String(60) FK   │ ✅ MIGRATED     │
└─────────────────────┴─────────────────┴─────────────────┴─────────────────┘
    """)

def show_usage_examples():
    """Show usage examples for the new Output model"""
    print("New Output Model Usage Examples:")
    print("=" * 50)
    print("""
# Creating a new Output
output = Output()
output.predicted_count = 5
output.pred_confidence = 0.85  # 85% confidence
output.object_type_id = "uuid-of-object-type"
output.input_id = "uuid-of-input"

# Saving to database
engine.new(output)
engine.save()

# Retrieving with confidence
retrieved = engine.get(Output, id=output.id)
print(f"Predicted: {retrieved.predicted_count}")
print(f"Confidence: {retrieved.pred_confidence * 100}%")

# Adding correction
retrieved.corrected_count = 7
engine.save()

# Querying by confidence
high_conf_outputs = [o for o in engine.get_all(Output) 
                    if o.pred_confidence > 0.9]
    """)

def main():
    """Main comparison function"""
    print("Output Model Migration Comparison")
    print("=" * 60)
    
    show_old_output_model()
    print()
    show_new_output_model()
    print()
    show_field_comparison()
    print()
    show_migration_benefits()
    print()
    show_usage_examples()
    
    print("=" * 60)
    print("Ready to test the new Output model!")

if __name__ == "__main__":
    main()
