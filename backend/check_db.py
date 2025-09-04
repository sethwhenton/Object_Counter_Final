#!/usr/bin/env python3
"""
Check database structure and relationships
"""

from simple_server import app
from models.database import db, Input, Output, ObjectType

def check_database():
    """Check database tables and relationships"""
    with app.app_context():
        print("📊 DATABASE STRUCTURE CHECK")
        print("=" * 50)
        
        # Get all records
        inputs = Input.query.all()
        outputs = Output.query.all()
        object_types = ObjectType.query.all()
        
        print(f"📈 Record Counts:")
        print(f"   Inputs: {len(inputs)}")
        print(f"   Outputs: {len(outputs)}")
        print(f"   Object Types: {len(object_types)}")
        print()
        
        # Check Input records
        print(f"📄 Input Records:")
        for i, input_rec in enumerate(inputs[:3], 1):
            print(f"   {i}. ID={input_rec.id}, image_path='{input_rec.image_path}'")
        print()
        
        # Check Output records
        print(f"📄 Output Records:")
        for i, output_rec in enumerate(outputs[:3], 1):
            print(f"   {i}. ID={output_rec.id}, input_fk={output_rec.input_fk}, object_type_fk={output_rec.object_type_fk}, predicted_count={output_rec.predicted_count}")
        print()
        
        # Check ObjectType records
        print(f"📄 Object Type Records:")
        for i, obj_type in enumerate(object_types[:3], 1):
            print(f"   {i}. ID={obj_type.id}, name='{obj_type.name}'")
        print()
        
        # Test the join query manually
        print(f"🔗 Testing Join Query:")
        query = db.session.query(Output, Input, ObjectType).join(
            Input, Output.input_fk == Input.id
        ).join(
            ObjectType, Output.object_type_fk == ObjectType.id
        )
        
        results = query.all()
        print(f"   Join Results: {len(results)} records")
        
        if results:
            for i, (output, input_rec, obj_type) in enumerate(results[:2], 1):
                print(f"   {i}. Output.id={output.id}, Input.image_path='{input_rec.image_path}', ObjectType.name='{obj_type.name}'")
        else:
            print("   ⚠️  No join results - checking relationships...")
            
            # Check if there are orphaned records
            for output in outputs[:2]:
                input_rec = Input.query.get(output.input_fk)
                if input_rec:
                    obj_type = ObjectType.query.get(output.object_type_fk)
                    print(f"   Manual join: Output.id={output.id} -> Input.image_path='{input_rec.image_path}' -> ObjectType.name='{obj_type.name if obj_type else 'NULL'}'")
                else:
                    print(f"   ⚠️  Output.id={output.id} has no matching Input record")

if __name__ == "__main__":
    check_database()
