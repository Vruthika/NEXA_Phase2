from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.offer import Offer
from datetime import datetime

class OfferCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, offer_id: int) -> Offer:
        return self.db.query(Offer).filter(Offer.offer_id == offer_id).first()
    
    def get_by_plan_id(self, plan_id: int):
        return self.db.query(Offer).filter(Offer.plan_id == plan_id).all()
    
    def get_active_offers(self):
        now = datetime.utcnow()
        return self.db.query(Offer).filter(
            and_(
                Offer.valid_from <= now,
                Offer.valid_until >= now
            )
        ).all()
    
    def create(self, offer_data: dict) -> Offer:
        offer = Offer(**offer_data)
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer
    
    def update(self, offer_id: int, offer_data: dict) -> Offer:
        offer = self.get_by_id(offer_id)
        if offer:
            for key, value in offer_data.items():
                setattr(offer, key, value)
            self.db.commit()
            self.db.refresh(offer)
        return offer
    
    def delete(self, offer_id: int) -> bool:
        offer = self.get_by_id(offer_id)
        if offer:
            self.db.delete(offer)
            self.db.commit()
            return True
        return False