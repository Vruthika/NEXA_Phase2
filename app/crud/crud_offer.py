from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from app.models.models import Offer, Plan
from app.schemas.offer import OfferCreate, OfferUpdate, OfferStatus

class CRUDOffer:
    def get(self, db: Session, offer_id: int):
        return db.query(Offer).filter(Offer.offer_id == offer_id).first()
    
    def get_by_plan(self, db: Session, plan_id: int, skip: int = 0, limit: int = 100):
        return db.query(Offer).filter(Offer.plan_id == plan_id).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, plan_id: int = None, status: str = None):
        query = db.query(Offer)
        
        if plan_id:
            query = query.filter(Offer.plan_id == plan_id)
        
        if status:
            current_time = datetime.utcnow()
            if status == "active":
                query = query.filter(
                    Offer.valid_from <= current_time,
                    Offer.valid_until >= current_time
                )
            elif status == "inactive":
                query = query.filter(Offer.valid_from > current_time)
            elif status == "expired":
                query = query.filter(Offer.valid_until < current_time)
            
        return query.offset(skip).limit(limit).all()
    
    def get_active_offers(self, db: Session):
        current_time = datetime.utcnow()
        return db.query(Offer).filter(
            Offer.valid_from <= current_time,
            Offer.valid_until >= current_time
        ).all()
    
    def calculate_offer_status(self, offer: Offer) -> OfferStatus:
        current_time = datetime.utcnow()
        if current_time < offer.valid_from:
            return OfferStatus.inactive
        elif current_time > offer.valid_until:
            return OfferStatus.expired
        else:
            return OfferStatus.active
    
    def create(self, db: Session, offer: OfferCreate):
        # Verify plan exists
        plan = db.query(Plan).filter(Plan.plan_id == offer.plan_id).first()
        if not plan:
            return None
        
        # Check if discounted price is less than plan price
        if offer.discounted_price >= plan.price:
            return None
        
        # Convert string dates to datetime objects
        valid_from = datetime.strptime(offer.valid_from, '%d.%m.%Y %H:%M')
        valid_until = datetime.strptime(offer.valid_until, '%d.%m.%Y %H:%M')
        
        db_offer = Offer(
            plan_id=offer.plan_id,
            offer_name=offer.offer_name,
            description=offer.description,
            discounted_price=offer.discounted_price,
            valid_from=valid_from,
            valid_until=valid_until
        )
        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer
    
    def update(self, db: Session, offer_id: int, offer_update: OfferUpdate):
        db_offer = self.get(db, offer_id)
        if db_offer:
            update_data = offer_update.model_dump(exclude_unset=True)
            
            # Convert string dates to datetime objects if provided
            if 'valid_from' in update_data and update_data['valid_from']:
                update_data['valid_from'] = datetime.strptime(update_data['valid_from'], '%d.%m.%Y %H:%M')
            if 'valid_until' in update_data and update_data['valid_until']:
                update_data['valid_until'] = datetime.strptime(update_data['valid_until'], '%d.%m.%Y %H:%M')
            
            for field, value in update_data.items():
                setattr(db_offer, field, value)
            db.commit()
            db.refresh(db_offer)
        return db_offer
    
    def delete(self, db: Session, offer_id: int):
        db_offer = self.get(db, offer_id)
        if db_offer:
            db.delete(db_offer)
            db.commit()
        return db_offer
    
    # def calculate_discount_percentage(self, db: Session, offer_id: int):
    #     offer = self.get(db, offer_id)
    #     if not offer:
    #         return None
    #     plan = db.query(Plan).filter(Plan.plan_id == offer.plan_id).first()
    #     if not plan:
    #         return None
    #     discount = ((plan.price - offer.discounted_price) / plan.price) * 100
    #     return round(discount, 2)

# Create instance
crud_offer = CRUDOffer()