from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.active_topup import ActiveTopupCreate, ActiveTopupResponse
from app.services.active_topup_service import ActiveTopupService

router = APIRouter()

@router.post("/", response_model=ActiveTopupResponse, status_code=status.HTTP_201_CREATED)
async def create_active_topup(
    topup_data: ActiveTopupCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    topup_service = ActiveTopupService(db)
    return topup_service.create_active_topup(current_customer.customer_id, topup_data)

@router.get("/my-topups", response_model=List[ActiveTopupResponse])
async def get_my_topups(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    topup_service = ActiveTopupService(db)
    return topup_service.get_customer_topups(current_customer.customer_id)

@router.get("/{topup_id}", response_model=ActiveTopupResponse)
async def get_topup_by_id(
    topup_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    topup_service = ActiveTopupService(db)
    topup = topup_service.get_topup_by_id(topup_id)
    
    # Verify topup belongs to current customer
    if topup.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this topup"
        )
    
    return topup

@router.post("/{topup_id}/update-usage")
async def update_topup_usage(
    topup_id: int,
    data_used_gb: float,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    topup_service = ActiveTopupService(db)
    topup = topup_service.get_topup_by_id(topup_id)
    
    # Verify topup belongs to current customer
    if topup.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this topup"
        )
    
    updated_topup = topup_service.update_data_usage(topup_id, data_used_gb)
    
    return {
        "message": "Topup data usage updated successfully",
        "topup_id": topup_id,
        "data_used_gb": data_used_gb,
        "remaining_data_gb": float(updated_topup.data_remaining_gb),
        "status": updated_topup.status.value
    }

@router.post("/{topup_id}/activate")
async def activate_topup(
    topup_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    topup_service = ActiveTopupService(db)
    topup = topup_service.get_topup_by_id(topup_id)
    
    # Verify topup belongs to current customer
    if topup.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to activate this topup"
        )
    
    updated_topup = topup_service.activate_topup(topup_id)
    
    return {
        "message": "Topup activated successfully",
        "topup_id": topup_id,
        "status": updated_topup.status.value,
        "activation_date": updated_topup.activation_date.isoformat()
    }