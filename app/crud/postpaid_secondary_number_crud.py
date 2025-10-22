from sqlalchemy.orm import Session
from app.models.postpaid_secondary_number import PostpaidSecondaryNumber

class PostpaidSecondaryNumberCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, secondary_id: int) -> PostpaidSecondaryNumber:
        return self.db.query(PostpaidSecondaryNumber).filter(PostpaidSecondaryNumber.secondary_id == secondary_id).first()
    
    def get_by_activation_id(self, activation_id: int):
        return self.db.query(PostpaidSecondaryNumber).filter(PostpaidSecondaryNumber.activation_id == activation_id).all()
    
    def get_by_phone_number(self, phone_number: str):
        return self.db.query(PostpaidSecondaryNumber).filter(PostpaidSecondaryNumber.phone_number == phone_number).first()
    
    def create(self, secondary_data: dict) -> PostpaidSecondaryNumber:
        secondary = PostpaidSecondaryNumber(**secondary_data)
        self.db.add(secondary)
        self.db.commit()
        self.db.refresh(secondary)
        return secondary
    
    def update(self, secondary_id: int, secondary_data: dict) -> PostpaidSecondaryNumber:
        secondary = self.get_by_id(secondary_id)
        if secondary:
            for key, value in secondary_data.items():
                setattr(secondary, key, value)
            self.db.commit()
            self.db.refresh(secondary)
        return secondary
    
    def delete(self, secondary_id: int) -> bool:
        secondary = self.get_by_id(secondary_id)
        if secondary:
            self.db.delete(secondary)
            self.db.commit()
            return True
        return False