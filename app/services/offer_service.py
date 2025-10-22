from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.crud.offer_crud import OfferCRUD
from app.crud.plan_crud import PlanCRUD
from app.schemas.offer import OfferCreate, OfferUpdate

class OfferService:
    def __init__(self, db: Session):
        self.db = db
        self.offer_crud = OfferCRUD(db)
        self.plan_crud = PlanCRUD(db)
    
    def create_offer(self, offer_data: OfferCreate):
        # Verify plan exists
        plan = self.plan_crud.get_by_id(offer_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Check if discounted price is less than plan price
        if offer_data.discounted_price >= plan.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discounted price must be less than original price"
            )
        
        return self.offer_crud.create(offer_data.dict())
    
    def get_offer_by_id(self, offer_id: int):
        offer = self.offer_crud.get_by_id(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        return offer
    
    def get_active_offers(self):
        return self.offer_crud.get_active_offers()
    
    def get_offers_by_plan(self, plan_id: int):
        plan = self.plan_crud.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return self.offer_crud.get_by_plan_id(plan_id)
    
    def update_offer(self, offer_id: int, offer_data: OfferUpdate):
        offer = self.get_offer_by_id(offer_id)
        return self.offer_crud.update(offer_id, offer_data.dict(exclude_unset=True))
    
    def delete_offer(self, offer_id: int):
        offer = self.get_offer_by_id(offer_id)
        return self.offer_crud.delete(offer_id)