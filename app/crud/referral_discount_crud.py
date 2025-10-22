from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.referral_discount import ReferralDiscount
from datetime import datetime

class ReferralDiscountCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, discount_id: int) -> ReferralDiscount:
        return self.db.query(ReferralDiscount).filter(ReferralDiscount.discount_id == discount_id).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(ReferralDiscount).filter(ReferralDiscount.customer_id == customer_id).all()
    
    def get_active_discounts(self, customer_id: int):
        return self.db.query(ReferralDiscount).filter(
            and_(
                ReferralDiscount.customer_id == customer_id,
                ReferralDiscount.is_used == False,
                ReferralDiscount.valid_until > datetime.utcnow()
            )
        ).all()
    
    def create(self, discount_data: dict) -> ReferralDiscount:
        discount = ReferralDiscount(**discount_data)
        self.db.add(discount)
        self.db.commit()
        self.db.refresh(discount)
        return discount
    
    def update(self, discount_id: int, discount_data: dict) -> ReferralDiscount:
        discount = self.get_by_id(discount_id)
        if discount:
            for key, value in discount_data.items():
                setattr(discount, key, value)
            self.db.commit()
            self.db.refresh(discount)
        return discount
    
    def mark_as_used(self, discount_id: int) -> ReferralDiscount:
        discount = self.get_by_id(discount_id)
        if discount:
            discount.is_used = True
            discount.used_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(discount)
        return discount