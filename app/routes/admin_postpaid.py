from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.models import Admin, PostpaidActivation, Customer, Plan, PostpaidDataAddon, PostpaidSecondaryNumber, Transaction, PostpaidStatus
from app.core.auth import get_current_admin
from app.schemas.postpaid import *
from app.crud import crud_postpaid

router = APIRouter(prefix="/postpaid", tags=["Postpaid Activations Management"])

# ==========================================================
# POSTPAID ACTIVATION MANAGEMENT
# ==========================================================

@router.get("/activations", response_model=List[PostpaidActivationDetailResponse])
async def get_all_postpaid_activations(
    plan_id: Optional[int] = Query(None, description="Filter by plan"),
    status: Optional[PostpaidStatus] = Query(None, description="Filter by status"),
    customer_phone: Optional[str] = Query(None, description="Filter by customer phone"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all current postpaid activations with filtering options.
    Shows only active activations by default.
    """
    # If no status filter provided, default to showing only active activations
    if status is None:
        status = PostpaidStatus.active
    
    filter_params = PostpaidActivationFilter(
        plan_id=plan_id,
        status=status,
        customer_phone=customer_phone,
        date_from=date_from,
        date_to=date_to
    )
    
    activations = crud_postpaid.get_all_activations(db, filter=filter_params, skip=skip, limit=limit)
    
    response_activations = []
    for activation in activations:
        customer = db.query(Customer).filter(Customer.customer_id == activation.customer_id).first()
        plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
        secondary_numbers = crud_postpaid.get_secondary_numbers(db, activation.activation_id)
        data_addons = crud_postpaid.get_active_addons(db, activation.activation_id)
        
        # Format secondary numbers
        secondary_responses = []
        for secondary in secondary_numbers:
            secondary_responses.append(SecondaryNumberResponse(
                secondary_id=secondary.secondary_id,
                phone_number=secondary.phone_number,
                added_date=secondary.added_date
            ))
        
        # Format data addons
        addon_responses = []
        for addon in data_addons:
            addon_responses.append(DataAddonResponse(
                addon_id=addon.addon_id,
                addon_name=addon.addon_name,
                data_amount_gb=float(addon.data_amount_gb),
                addon_price=float(addon.addon_price),
                purchased_date=addon.purchased_date,
                valid_until=addon.valid_until,
                status=addon.status
            ))
        
        response_activations.append(PostpaidActivationDetailResponse(
            activation_id=activation.activation_id,
            customer_id=activation.customer_id,
            customer_name=customer.full_name if customer else "Unknown",
            customer_phone=customer.phone_number if customer else "Unknown",
            plan_name=plan.plan_name if plan else "Unknown",
            primary_number=activation.primary_number,
            billing_cycle_start=activation.billing_cycle_start,
            billing_cycle_end=activation.billing_cycle_end,
            base_data_allowance_gb=float(activation.base_data_allowance_gb),
            current_data_balance_gb=float(activation.current_data_balance_gb),
            data_used_gb=float(activation.data_used_gb),
            base_amount=float(activation.base_amount),
            total_amount_due=float(activation.total_amount_due),
            status=activation.status,
            secondary_numbers=secondary_responses,
            data_addons=addon_responses
        ))
    
    return response_activations

@router.get("/activations/{activation_id}", response_model=PostpaidActivationDetailResponse)
async def get_postpaid_activation_details(
    activation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific postpaid activation.
    """
    activation = crud_postpaid.get_activation_by_id(db, activation_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postpaid activation not found"
        )
    
    customer = db.query(Customer).filter(Customer.customer_id == activation.customer_id).first()
    plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
    secondary_numbers = crud_postpaid.get_secondary_numbers(db, activation.activation_id)
    data_addons = crud_postpaid.get_active_addons(db, activation.activation_id)
    
    # Format secondary numbers
    secondary_responses = []
    for secondary in secondary_numbers:
        secondary_responses.append(SecondaryNumberResponse(
            secondary_id=secondary.secondary_id,
            phone_number=secondary.phone_number,
            added_date=secondary.added_date
        ))
    
    # Format data addons
    addon_responses = []
    for addon in data_addons:
        addon_responses.append(DataAddonResponse(
            addon_id=addon.addon_id,
            addon_name=addon.addon_name,
            data_amount_gb=float(addon.data_amount_gb),
            addon_price=float(addon.addon_price),
            purchased_date=addon.purchased_date,
            valid_until=addon.valid_until,
            status=addon.status
        ))
    
    return PostpaidActivationDetailResponse(
        activation_id=activation.activation_id,
        customer_id=activation.customer_id,
        customer_name=customer.full_name if customer else "Unknown",
        customer_phone=customer.phone_number if customer else "Unknown",
        plan_name=plan.plan_name if plan else "Unknown",
        primary_number=activation.primary_number,
        billing_cycle_start=activation.billing_cycle_start,
        billing_cycle_end=activation.billing_cycle_end,
        base_data_allowance_gb=float(activation.base_data_allowance_gb),
        current_data_balance_gb=float(activation.current_data_balance_gb),
        data_used_gb=float(activation.data_used_gb),
        base_amount=float(activation.base_amount),
        total_amount_due=float(activation.total_amount_due),
        status=activation.status,
        secondary_numbers=secondary_responses,
        data_addons=addon_responses
    )

# ==========================================================
# DATA ADDON MANAGEMENT
# ==========================================================

@router.get("/addons/{activation_id}")
async def get_activation_addons(
    activation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all data addons for a specific activation.
    """
    activation = crud_postpaid.get_activation_by_id(db, activation_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postpaid activation not found"
        )
    
    addons = db.query(PostpaidDataAddon).filter(
        PostpaidDataAddon.activation_id == activation_id
    ).all()
    
    response_addons = []
    for addon in addons:
        response_addons.append(DataAddonResponse(
            addon_id=addon.addon_id,
            addon_name=addon.addon_name,
            data_amount_gb=float(addon.data_amount_gb),
            addon_price=float(addon.addon_price),
            purchased_date=addon.purchased_date,
            valid_until=addon.valid_until,
            status=addon.status
        ))
    
    return response_addons

# ==========================================================
# SECONDARY NUMBER MANAGEMENT
# ==========================================================

@router.get("/activations/{activation_id}/secondary-validation")
async def validate_secondary_number_addition(
    activation_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Check if a secondary number can be added to this activation
    """
    activation = crud_postpaid.get_activation_by_id(db, activation_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postpaid activation not found"
        )
    
    plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
    current_count = db.query(PostpaidSecondaryNumber).filter(
        PostpaidSecondaryNumber.activation_id == activation_id
    ).count()
    
    return {
        "activation_id": activation_id,
        "plan_name": plan.plan_name if plan else "Unknown",
        "max_secondary_numbers_allowed": getattr(plan, 'max_secondary_numbers', 0),
        "current_secondary_numbers": current_count,
        "can_add_more": current_count < (getattr(plan, 'max_secondary_numbers', 0)),
        "remaining_slots": max(0, (getattr(plan, 'max_secondary_numbers', 0) - current_count))
    }


router1 = APIRouter(prefix="/postpaid", tags=["Postpaid Billing Management"])

# ==========================================================
# BILLING & PAYMENTS
# ==========================================================

@router1.get("/due-payments")
async def get_due_payments(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all activations with due payments (only unpaid bills).
    """
    activations = crud_postpaid.get_due_payments(db)
    
    response_activations = []
    for activation in activations:
        customer = db.query(Customer).filter(Customer.customer_id == activation.customer_id).first()
        plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
        
        response_activations.append({
            "activation_id": activation.activation_id,
            "customer_name": customer.full_name if customer else "Unknown",
            "customer_phone": customer.phone_number if customer else "Unknown",
            "plan_name": plan.plan_name if plan else "Unknown",
            "primary_number": activation.primary_number,
            "total_amount_due": float(activation.total_amount_due),
            "billing_cycle_end": activation.billing_cycle_end,
            "days_remaining": (activation.billing_cycle_end - datetime.utcnow()).days
        })
    
    return response_activations

# ==========================================================
# MONITORING & REPORTS
# ==========================================================

@router1.get("/customer-history/{customer_id}")
async def get_customer_postpaid_history(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed postpaid history for a specific customer.
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get all activations for this customer
    activations = db.query(PostpaidActivation).filter(
        PostpaidActivation.customer_id == customer_id
    ).order_by(PostpaidActivation.created_at.desc()).all()
    
    # Get all postpaid bill payments
    transactions = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.transaction_type == "postpaid_bill_payment"
    ).order_by(Transaction.transaction_date.desc()).all()
    
    response_activations = []
    for activation in activations:
        plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
        secondary_numbers = crud_postpaid.get_secondary_numbers(db, activation.activation_id)
        data_addons = crud_postpaid.get_active_addons(db, activation.activation_id)
        
        response_activations.append({
            "activation_id": activation.activation_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "primary_number": activation.primary_number,
            "status": activation.status,
            "billing_cycle_start": activation.billing_cycle_start,
            "billing_cycle_end": activation.billing_cycle_end,
            "total_amount_due": float(activation.total_amount_due),
            "data_used_gb": float(activation.data_used_gb),
            "secondary_numbers_count": len(secondary_numbers),
            "active_addons_count": len(data_addons),
            "created_at": activation.created_at
        })
    
    response_transactions = []
    for transaction in transactions:
        plan = db.query(Plan).filter(Plan.plan_id == transaction.plan_id).first()
        response_transactions.append({
            "transaction_id": transaction.transaction_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "amount": float(transaction.final_amount),
            "payment_method": transaction.payment_method,
            "payment_status": transaction.payment_status,
            "transaction_date": transaction.transaction_date
        })
    
    return {
        "customer": {
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "phone_number": customer.phone_number
        },
        "activations": response_activations,
        "payment_history": response_transactions
    }