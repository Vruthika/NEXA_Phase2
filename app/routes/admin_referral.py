from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Admin, ReferralStatus
from app.core.auth import get_current_admin
from app.schemas.referral import ReferralProgramResponse, ReferralUsageLogResponse, SystemReferralStats
from app.crud.crud_referral import crud_referral

router = APIRouter(prefix="/admin/referrals", tags=["Admin - Referral Management"])

@router.get("/", response_model=List[ReferralProgramResponse])
async def get_all_referral_programs(
    status: Optional[ReferralStatus] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: View all referral programs with filtering.
    """
    referral_programs = crud_referral.get_all_referral_programs(
        db, skip=skip, limit=limit, status=status, is_active=is_active
    )
    return referral_programs

@router.get("/{referral_id}/usage-logs", response_model=List[ReferralUsageLogResponse])
async def get_referral_usage_logs(
    referral_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: View usage logs for a specific referral program.
    """
    usage_logs = crud_referral.get_referral_usage_logs(db, referral_id)
    return usage_logs

@router.get("/stats/overview", response_model=SystemReferralStats)
async def get_referral_overview_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Get overview statistics for referral programs.
    """
    stats = crud_referral.get_system_referral_stats(db)
    return SystemReferralStats(**stats)


@router.get("/customer/{customer_id}/referrals")
async def get_customer_referral_details(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Get detailed referral information for a specific customer.
    """
    from app.models.models import Customer
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Get referral program details
    referral_program = crud_referral.get_referral_by_customer(db, customer_id)
    
    # Get referral discounts
    discounts = crud_referral.get_customer_referral_discounts(db, customer_id)
    
    # Get referral usage logs if program exists
    usage_logs = []
    if referral_program:
        usage_logs = crud_referral.get_referral_usage_logs(db, referral_program.referral_id)

    return {
        "customer": {
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "phone_number": customer.phone_number
        },
        "referral_program": referral_program,
        "active_discounts": discounts,
        "usage_logs": usage_logs
    }