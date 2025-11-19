from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.models import Customer
from app.core.auth import get_current_customer
from app.schemas.referral import *
from app.crud.crud_referral import crud_referral

router = APIRouter(prefix="/customer/referral", tags=["Customer Referral"])

@router.post("/generate", response_model=ReferralProgramResponse)
async def generate_referral_code(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Generate a new referral code for the current customer.
    """
    referral_program, error = crud_referral.create_referral_program(db, current_customer.customer_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return referral_program

@router.get("/my-referrals", response_model=ReferralStatsResponse)
async def get_referral_details(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get referral program details and statistics for the current customer.
    """
    stats = crud_referral.get_referral_stats(db, current_customer.customer_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active referral program found"
        )

    return ReferralStatsResponse(**stats)

@router.get("/discounts", response_model=List[ReferralDiscountResponse])
async def get_my_referral_discounts(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all active referral discounts for the current customer.
    """
    discounts = crud_referral.get_customer_referral_discounts(db, current_customer.customer_id)
    return discounts

