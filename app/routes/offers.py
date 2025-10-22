from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.offer import OfferCreate, OfferResponse, OfferUpdate
from app.services.offer_service import OfferService

router = APIRouter()

@router.get("/", response_model=List[OfferResponse])
async def get_all_offers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    offer_service = OfferService(db)
    return offer_service.get_active_offers()

@router.get("/active", response_model=List[OfferResponse])
async def get_active_offers(db: Session = Depends(get_db)):
    offer_service = OfferService(db)
    return offer_service.get_active_offers()

@router.get("/plan/{plan_id}", response_model=List[OfferResponse])
async def get_offers_by_plan(plan_id: int, db: Session = Depends(get_db)):
    offer_service = OfferService(db)
    return offer_service.get_offers_by_plan(plan_id)

@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer_by_id(offer_id: int, db: Session = Depends(get_db)):
    offer_service = OfferService(db)
    return offer_service.get_offer_by_id(offer_id)

@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    offer_data: OfferCreate,
    db: Session = Depends(get_db)
):
    offer_service = OfferService(db)
    return offer_service.create_offer(offer_data)

@router.put("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    db: Session = Depends(get_db)
):
    offer_service = OfferService(db)
    return offer_service.update_offer(offer_id, offer_data)

@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    offer_service = OfferService(db)
    offer_service.delete_offer(offer_id)
    return None