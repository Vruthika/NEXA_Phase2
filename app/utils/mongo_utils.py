from bson import ObjectId
from datetime import datetime
from typing import Any, Dict

def bson_to_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert BSON document to JSON serializable format"""
    print(f"bson_to_json input: {data}")
    
    if not data:
        print("bson_to_json: Input data is empty")
        return data
    
    result = {}
    for key, value in data.items():
        print(f"Processing key: {key}, value: {value}, type: {type(value)}")
        
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = bson_to_json(value)
        elif isinstance(value, list):
            result[key] = [bson_to_json(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    print(f"bson_to_json result: {result}")
    return result
def create_timestamps():
    """Create created_at and updated_at timestamps"""
    now = datetime.utcnow()
    return {"created_at": now, "updated_at": now}

def update_timestamp():
    """Create updated_at timestamp"""
    return {"updated_at": datetime.utcnow()}