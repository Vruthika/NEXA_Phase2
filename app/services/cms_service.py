from sqlalchemy.orm import Session
from app.database import mongodb

class CMSService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_header_content(self):
        # Get from MongoDB
        return mongodb.header_content.find_one() or {}
    
    def update_header_content(self, content_data: dict):
        # Update in MongoDB
        result = mongodb.header_content.update_one(
            {},
            {"$set": content_data},
            upsert=True
        )
        return {"message": "Header content updated successfully"}
    
    def get_carousel_items(self):
        # Get from MongoDB
        return list(mongodb.carousel_items.find().sort("order", 1))
    
    def update_carousel_item(self, item_data: dict):
        # Update in MongoDB
        result = mongodb.carousel_items.update_one(
            {"_id": item_data.get("_id")},
            {"$set": item_data},
            upsert=True
        )
        return {"message": "Carousel item updated successfully"}
    
    def get_faqs(self):
        # Get from MongoDB
        return list(mongodb.faqs.find().sort("order", 1))
    
    def update_faq(self, faq_data: dict):
        # Update in MongoDB
        result = mongodb.faqs.update_one(
            {"_id": faq_data.get("_id")},
            {"$set": faq_data},
            upsert=True
        )
        return {"message": "FAQ updated successfully"}