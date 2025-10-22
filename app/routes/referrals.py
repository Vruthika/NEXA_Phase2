from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.referral_program import ReferralProgramCreate, ReferralProgramResponse
from app.services.referral_service import ReferralService

router = APIRouter()

@router.post("/", response_model=ReferralProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referee_phone_number: str,
    max_uses: int = 1,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    return referral_service.create_referral(
        current_customer.customer_id,
        referee_phone_number,
        max_uses
    )

@router.post("/use/{referral_code}")
async def use_referral_code(
    referral_code: str,
    used_by_phone: str,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    result = referral_service.use_referral_code(
        referral_code,
        used_by_phone,
        current_customer.customer_id
    )
    
    return {
        "message": "Referral code used successfully",
        "referral_id": result["referral"].referral_id,
        "discount_id": result["discount"].discount_id,
        "discount_percentage": float(result["discount"].discount_percentage)
    }

@router.get("/my-referrals", response_model=List[ReferralProgramResponse])
async def get_my_referrals(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    return referral_service.get_customer_referrals(current_customer.customer_id)

@router.get("/my-discounts")
async def get_my_discounts(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    discounts = referral_service.get_customer_discounts(current_customer.customer_id)
    
    return {
        "discounts": [
            {
                "discount_id": discount.discount_id,
                "discount_percentage": float(discount.discount_percentage),
                "is_used": discount.is_used,
                "valid_until": discount.valid_until.isoformat(),
                "created_at": discount.created_at.isoformat()
            }
            for discount in discounts
        ]
    }

@router.post("/apply-discount/{discount_id}")
async def apply_referral_discount(
    discount_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    discount = referral_service.apply_referral_discount(discount_id, current_customer.customer_id)
    
    return {
        "message": "Discount applied successfully",
        "discount_id": discount.discount_id,
        "discount_percentage": float(discount.discount_percentage)
    }

@router.get("/stats")
async def get_referral_stats(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    referral_service = ReferralService(db)
    stats = referral_service.get_referral_stats(current_customer.customer_id)
    
    return stats