from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.models import Customer, Plan, PostpaidActivation, PostpaidDataAddon, PostpaidSecondaryNumber, Transaction
from app.core.auth import get_current_customer
from app.schemas.postpaid import *
from app.crud import crud_postpaid


# ==========================================================
# POSTPAID PLAN BROWSING
# ==========================================================
plans_addons_router = APIRouter(prefix="/customer/postpaid", tags=["View Postpaid Plans & Addons"])


@plans_addons_router.get("/plans", response_model=List[PostpaidPlanResponse])
async def get_postpaid_plans(
    plan_id: Optional[int] = Query(None, description="Get specific postpaid plan by ID"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all available postpaid plans or a specific postpaid plan by ID.
    """
    # If plan_id is provided, return only that specific postpaid plan
    if plan_id is not None:
        plan = db.query(Plan).filter(
            Plan.plan_id == plan_id,
            Plan.plan_type == "postpaid",
            Plan.status == "active",
            Plan.deleted_at.is_(None)
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Postpaid plan not found"
            )
        
        return [plan]
    
    # If no plan_id provided, return all postpaid plans
    plans = db.query(Plan).filter(
        Plan.plan_type == "postpaid",
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    ).all()
    
    return plans

@plans_addons_router.get("/usage", response_model=PostpaidUsageResponse)
async def get_data_usage(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current data usage statistics.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    response_data = {
        "activation_id": activation.activation_id,
        "data_used_gb": float(activation.data_used_gb),
        "current_data_balance_gb": float(activation.current_data_balance_gb),
        "base_data_allowance_gb": float(activation.base_data_allowance_gb)
    }
    
    return PostpaidUsageResponse(**response_data)

@plans_addons_router.get("/addon-plans", response_model=List[PostpaidPlanResponse])
async def get_data_addon_plans(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all available data addon plans (postpaid plans with is_topup=True).
    """
    addon_plans = db.query(Plan).filter(
        Plan.plan_type == "postpaid",
        Plan.is_topup == True,
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    ).all()
    
    return addon_plans

@plans_addons_router.post("/purchase-addon", response_model=DataAddonResponse)
async def purchase_data_addon(
    addon_data: DataAddonPurchaseRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Purchase a data addon for postpaid plan.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    if activation.activation_id != addon_data.activation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activation ID"
        )
    
    # Verify the addon plan exists and is a valid addon
    addon_plan = db.query(Plan).filter(
        Plan.plan_id == addon_data.plan_id,
        Plan.plan_type == "postpaid",
        Plan.is_topup == True,
        Plan.status == "active"
    ).first()
    
    if not addon_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon plan not found or inactive"
        )
    
    # Convert Decimal to float for the purchase function
    data_amount_gb = float(addon_plan.data_allowance_gb) if addon_plan.data_allowance_gb else 0.0
    addon_price = float(addon_plan.price)
    
    addon = crud_postpaid.purchase_data_addon(
        db, activation.activation_id, addon_plan.plan_name,
        data_amount_gb, addon_price
    )
    
    if not addon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to purchase data addon"
        )
    
    # Update addon validity to match billing cycle
    addon.valid_until = activation.billing_cycle_end
    db.commit()
    
    response_data = {
        "addon_id": addon.addon_id,
        "addon_name": addon.addon_name,
        "data_amount_gb": float(addon.data_amount_gb),
        "addon_price": float(addon.addon_price),
        "purchased_date": addon.purchased_date,
        "valid_until": addon.valid_until,
        "status": addon.status
    }
    
    return DataAddonResponse(**response_data)

@plans_addons_router.get("/addons", response_model=List[DataAddonResponse])
async def get_active_data_addons(  
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all active data addons for current postpaid plan.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    addons = crud_postpaid.get_active_addons(db, activation.activation_id)
    
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
# POSTPAID ACTIVATION
# ==========================================================

activations_router = APIRouter(prefix="/customer/postpaid", tags=["Postpaid Activations"])


@activations_router.post("/activate", response_model=PostpaidActivationResponse)
async def activate_postpaid_plan(
    activation_data: PostpaidActivationRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Activate a postpaid plan for a primary phone number.
    Note: Each phone number can have only one active postpaid plan at a time.
    """
    print(f"DEBUG: Activation request received - Customer: {current_customer.customer_id}, Plan: {activation_data.plan_id}, Number: {activation_data.primary_number}")
    
    activation, error_message = crud_postpaid.create_activation(
        db, current_customer.customer_id, 
        activation_data.plan_id, activation_data.primary_number
    )
    
    if not activation:
        error_detail = error_message or "Failed to activate postpaid plan"
        print(f"DEBUG: Activation failed - {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    # Get plan name for response
    plan = db.query(Plan).filter(Plan.plan_id == activation_data.plan_id).first()
    
    response_data = {
        "activation_id": activation.activation_id,
        "plan_name": plan.plan_name if plan else "Unknown",
        "primary_number": activation.primary_number,
        "billing_cycle_start": activation.billing_cycle_start,
        "billing_cycle_end": activation.billing_cycle_end,
        "base_data_allowance_gb": float(activation.base_data_allowance_gb),
        "current_data_balance_gb": float(activation.current_data_balance_gb),
        "data_used_gb": float(activation.data_used_gb),
        "base_amount": float(activation.base_amount),
        "total_amount_due": float(activation.total_amount_due),
        "status": activation.status
    }
    
    print(f"DEBUG: Activation successful - Activation ID: {activation.activation_id}")
    return PostpaidActivationResponse(**response_data)

@activations_router.get("/activation", response_model=List[PostpaidActivationResponse])
async def get_customer_postpaid_activations(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all active postpaid activations for the current customer.
    Includes activations where customer is primary owner OR secondary number.
    """
    # Get all activations where this customer is involved (primary or secondary)
    activations = crud_postpaid.get_activations_for_customer(
        db, 
        current_customer.customer_id, 
        current_customer.phone_number
    )
    
    if not activations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plans found for your account"
        )
    
    response_activations = []
    for activation in activations:
        plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
        
        # Get secondary numbers for this activation
        secondary_numbers = crud_postpaid.get_secondary_numbers(db, activation.activation_id)
        
        # Check if current customer is primary owner or secondary number
        is_primary_owner = (activation.customer_id == current_customer.customer_id)
        
        response_data = {
            "activation_id": activation.activation_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "primary_number": activation.primary_number,
            "billing_cycle_start": activation.billing_cycle_start,
            "billing_cycle_end": activation.billing_cycle_end,
            "base_data_allowance_gb": float(activation.base_data_allowance_gb),
            "current_data_balance_gb": float(activation.current_data_balance_gb),
            "data_used_gb": float(activation.data_used_gb),
            "base_amount": float(activation.base_amount),
            "total_amount_due": float(activation.total_amount_due),
            "status": activation.status,
            "secondary_numbers": [
                {
                    "secondary_id": sec.secondary_id,
                    "phone_number": sec.phone_number,
                    "added_date": sec.added_date
                } for sec in secondary_numbers
            ],
            "user_role": "primary_owner" if is_primary_owner else "secondary_number"
        }
        
        response_activations.append(PostpaidActivationResponse(**response_data))
    
    return response_activations


# ==========================================================
# BILLING
# ==========================================================

bill_router = APIRouter(prefix="/customer/postpaid", tags=["Postpaid Billing"])


@bill_router.get("/bill", response_model=PostpaidBillResponse)
async def get_postpaid_bill(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current postpaid bill details.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    bill_details = crud_postpaid.get_bill_details(db, activation.activation_id)
    
    response_data = {
        "activation_id": activation.activation_id,
        "billing_cycle_start": activation.billing_cycle_start,
        "billing_cycle_end": activation.billing_cycle_end,
        "base_amount": float(activation.base_amount),
        "addon_charges": bill_details["addon_charges"],
        "total_amount_due": bill_details["total_amount_due"],
        "due_date": activation.billing_cycle_end
    }
    
    return PostpaidBillResponse(**response_data)

@bill_router.post("/pay-bill")
async def pay_postpaid_bill(
    payment_data: BillPaymentRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Pay postpaid bill for a specific activation.
    Only allowed after billing cycle ends.
    """
    # First verify that this activation exists and is active
    activation = crud_postpaid.get_activation_by_id(db, payment_data.activation_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postpaid activation not found"
        )
    
    # Check if customer has access to this activation (primary or secondary)
    has_access = False
    
    # Check if primary owner
    if activation.customer_id == current_customer.customer_id:
        has_access = True
    # Check if secondary number
    else:
        secondary_link = db.query(PostpaidSecondaryNumber).filter(
            PostpaidSecondaryNumber.activation_id == payment_data.activation_id,
            PostpaidSecondaryNumber.customer_id == current_customer.customer_id
        ).first()
        if secondary_link:
            has_access = True
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pay bills for activations you own or are linked to"
        )
    
    transaction, error_message = crud_postpaid.process_bill_payment(
        db, payment_data.activation_id, payment_data.payment_method
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return {
        "message": "Bill payment successful", 
        "activation_id": activation.activation_id,
        "primary_number": activation.primary_number,
        "transaction_id": transaction.transaction_id
    }   


# ==========================================================
# SECONDARY NUMBERS
# ==========================================================

secondary_numbers_router = APIRouter(prefix="/customer/postpaid", tags=["Postpaid - Secondary Numbers"])


@secondary_numbers_router.post("/secondary-numbers", response_model=SecondaryNumberResponse)
async def add_secondary_number(
    secondary_data: SecondaryNumberRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Add a secondary number to postpaid plan.
    """
    print(f"DEBUG: Adding secondary number request - Activation: {secondary_data.activation_id}, Number: {secondary_data.phone_number}")
    
    # Verify the activation belongs to the current customer
    activation = crud_postpaid.get_activation_by_id(db, secondary_data.activation_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postpaid activation not found"
        )
    
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add secondary numbers to your own activations"
        )
    
    secondary = crud_postpaid.add_secondary_number(
        db, secondary_data.activation_id, secondary_data.phone_number, current_customer.customer_id
    )
    
    if not secondary:
        # Provide more specific error messages
        plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
        current_count = db.query(PostpaidSecondaryNumber).filter(
            PostpaidSecondaryNumber.activation_id == secondary_data.activation_id
        ).count()
        
        max_allowed = getattr(plan, 'max_secondary_numbers', 0)
        
        if max_allowed == 0:
            error_detail = "This plan does not support secondary numbers"
        elif current_count >= max_allowed:
            error_detail = f"Maximum secondary numbers ({max_allowed}) reached for this plan"
        else:
            error_detail = "Failed to add secondary number. It may already exist or there was a system error."
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    return SecondaryNumberResponse(
        secondary_id=secondary.secondary_id,
        phone_number=secondary.phone_number,
        added_date=secondary.added_date
    )

@secondary_numbers_router.delete("/secondary-numbers/{secondary_id}")
async def remove_secondary_number(
    secondary_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Remove a secondary number from postpaid plan.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    # Verify the secondary number belongs to this activation
    secondary = db.query(PostpaidSecondaryNumber).filter(
        PostpaidSecondaryNumber.secondary_id == secondary_id,
        PostpaidSecondaryNumber.activation_id == activation.activation_id
    ).first()
    
    if not secondary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secondary number not found"
        )
    
    result = crud_postpaid.remove_secondary_number(db, secondary_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove secondary number"
        )
    
    return {"message": "Secondary number removed successfully"}

@secondary_numbers_router.get("/secondary-numbers", response_model=List[SecondaryNumberResponse])
async def get_secondary_numbers(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all secondary numbers for current postpaid plan.
    """
    activation = crud_postpaid.get_activation_by_customer(db, current_customer.customer_id)
    if not activation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active postpaid plan found"
        )
    
    secondaries = crud_postpaid.get_secondary_numbers(db, activation.activation_id)
    
    response_secondaries = []
    for secondary in secondaries:
        response_secondaries.append(SecondaryNumberResponse(
            secondary_id=secondary.secondary_id,
            phone_number=secondary.phone_number,
            added_date=secondary.added_date
        ))
    
    return response_secondaries