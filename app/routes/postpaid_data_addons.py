from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.services.postpaid_activation_service import PostpaidActivationService

router = APIRouter()

@router.get("/activation/{activation_id}")
async def get_data_addons(
    activation_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    activation = postpaid_service.get_activation_by_id(activation_id)
    
    # Verify activation belongs to current customer
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this activation"
        )
    
    return activation.data_addons