from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.models import Customer, LinkedAccount, Plan, Transaction, Subscription
from app.core.auth import get_current_customer
from app.schemas.linked_account import *
from app.crud import crud_linked_account
from app.crud.crud_linked_account import crud_linked_account

router = APIRouter(prefix="/customer", tags=["Linked Accounts"])

@router.post("/linked-accounts", response_model=LinkedAccountResponse)
async def add_linked_account(
    linked_data: LinkedAccountBase,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Add a linked account (family member/friend) to your account.
    The linked phone number will receive OTP for verification (simulated).
    """
    print(f"DEBUG: Adding linked account - Primary: {current_customer.customer_id}, Linked: {linked_data.linked_phone_number}")
    
    # Create the linked account data with primary customer ID
    linked_account_data = LinkedAccountCreate(
        primary_customer_id=current_customer.customer_id,
        linked_phone_number=linked_data.linked_phone_number
    )
    
    # Create the linked account
    linked_account, error_message = crud_linked_account.create(db, linked_account_data)
    
    if not linked_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Failed to add linked account"
        )
    
    # Get additional details for response
    linked_customer = None
    if linked_account.linked_customer_id:
        linked_customer = db.query(Customer).filter(
            Customer.customer_id == linked_account.linked_customer_id
        ).first()
    
    response_data = {
        "linked_account_id": linked_account.linked_account_id,
        "primary_customer_id": linked_account.primary_customer_id,
        "linked_phone_number": linked_account.linked_phone_number,
        "linked_customer_id": linked_account.linked_customer_id,
        "created_at": linked_account.created_at,
        "primary_customer_name": current_customer.full_name,
        "linked_customer_name": linked_customer.full_name if linked_customer else None,
        "is_registered_user": linked_account.linked_customer_id is not None
    }
    
    return LinkedAccountResponse(**response_data)

@router.get("/linked-accounts", response_model=List[LinkedAccountResponse])
async def get_linked_accounts(
    linked_account_id: Optional[int] = Query(None, description="Get specific linked account by ID"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all linked accounts for the current customer or a specific linked account by ID.
    """
    # If linked_account_id is provided, return only that specific linked account
    if linked_account_id is not None:
        # Verify the linked account belongs to current customer
        linked_account = crud_linked_account.get_by_id(db, linked_account_id)
        if not linked_account or linked_account.primary_customer_id != current_customer.customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked account not found"
            )
        
        # Get linked customer details if exists
        linked_customer = None
        if linked_account.linked_customer_id:
            linked_customer = db.query(Customer).filter(
                Customer.customer_id == linked_account.linked_customer_id
            ).first()
        
        return [LinkedAccountResponse(
            linked_account_id=linked_account.linked_account_id,
            primary_customer_id=linked_account.primary_customer_id,
            linked_phone_number=linked_account.linked_phone_number,
            linked_customer_id=linked_account.linked_customer_id,
            created_at=linked_account.created_at,
            primary_customer_name=current_customer.full_name,
            linked_customer_name=linked_customer.full_name if linked_customer else None,
            is_registered_user=linked_account.linked_customer_id is not None
        )]
    
    # If no linked_account_id provided, return all linked accounts for the current customer
    linked_accounts = crud_linked_account.get_by_primary_customer(db, current_customer.customer_id)
    
    response_accounts = []
    for account in linked_accounts:
        # Get linked customer details if exists
        linked_customer = None
        if account.linked_customer_id:
            linked_customer = db.query(Customer).filter(
                Customer.customer_id == account.linked_customer_id
            ).first()
        
        response_accounts.append(LinkedAccountResponse(
            linked_account_id=account.linked_account_id,
            primary_customer_id=account.primary_customer_id,
            linked_phone_number=account.linked_phone_number,
            linked_customer_id=account.linked_customer_id,
            created_at=account.created_at,
            primary_customer_name=current_customer.full_name,
            linked_customer_name=linked_customer.full_name if linked_customer else None,
            is_registered_user=account.linked_customer_id is not None
        ))
    
    return response_accounts

@router.delete("/linked-accounts/{linked_account_id}")
async def remove_linked_account(
    linked_account_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Remove a linked account from your account.
    """
    success = crud_linked_account.delete(db, linked_account_id, current_customer.customer_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked account not found or you don't have permission to remove it"
        )
    
    return {"message": "Linked account removed successfully"}

@router.post("/linked-accounts/{linked_account_id}/recharge", response_model=RechargeLinkedResponse)
async def recharge_linked_account(
    linked_account_id: int,
    recharge_data: RechargeLinkedRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Recharge a plan for a linked account.
    """
    # Verify the linked account belongs to current customer
    linked_account = crud_linked_account.get_by_id(db, linked_account_id)
    if not linked_account or linked_account.primary_customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked account not found"
        )
    
    # Verify plan exists and is active
    plan = db.query(Plan).filter(
        Plan.plan_id == recharge_data.plan_id,
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive"
        )
    
    # Verify offer if provided
    offer = None
    if recharge_data.offer_id and recharge_data.offer_id > 0:
        from app.models.models import Offer
        offer = db.query(Offer).filter(
            Offer.offer_id == recharge_data.offer_id,
            Offer.plan_id == recharge_data.plan_id,
            Offer.valid_from <= datetime.utcnow(),
            Offer.valid_until >= datetime.utcnow()
        ).first()
        
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found or expired"
            )
    
    # Calculate amounts
    original_amount = float(plan.price)
    discount_amount = 0.0
    
    if offer:
        discounted_price = float(offer.discounted_price)
        discount_amount = original_amount - discounted_price
        final_amount = discounted_price
    else:
        final_amount = original_amount
    
    # Create transaction for the linked number
    transaction = Transaction(
        customer_id=current_customer.customer_id,  
        plan_id=recharge_data.plan_id,
        offer_id=recharge_data.offer_id if recharge_data.offer_id and recharge_data.offer_id > 0 else None,
        recipient_phone_number=linked_account.linked_phone_number, 
        transaction_type="prepaid_recharge",
        original_amount=original_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        payment_method=recharge_data.payment_method,
        payment_status="success"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    from app.services.subscription_service import subscription_service
    from datetime import timedelta
    
    current_time = datetime.utcnow()
    
    # Check if linked number has active subscriptions
    active_subscriptions = db.query(Subscription).filter(
        Subscription.phone_number == linked_account.linked_phone_number,
        Subscription.expiry_date > current_time
    ).order_by(Subscription.expiry_date.desc()).all()
    
    if plan.is_topup or not active_subscriptions:
        activation_date = current_time
        expiry_date = current_time + timedelta(days=plan.validity_days)
        
        subscription = Subscription(
            customer_id=linked_account.linked_customer_id or current_customer.customer_id,
            phone_number=linked_account.linked_phone_number,
            plan_id=recharge_data.plan_id,
            transaction_id=transaction.transaction_id,
            is_topup=plan.is_topup,
            activation_date=activation_date,
            expiry_date=expiry_date,
            data_balance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=current_time
        )
        
        db.add(subscription)
        db.commit()
        
        message = f"Recharge successful for {linked_account.linked_phone_number}! Plan activated immediately."
        
    else:
        latest_active_subscription = active_subscriptions[0]
        activation_date = latest_active_subscription.expiry_date
        expiry_date = activation_date + timedelta(days=plan.validity_days)
        
        subscription = Subscription(
            customer_id=linked_account.linked_customer_id or current_customer.customer_id,
            phone_number=linked_account.linked_phone_number,
            plan_id=recharge_data.plan_id,
            transaction_id=transaction.transaction_id,
            is_topup=plan.is_topup,
            activation_date=activation_date,
            expiry_date=expiry_date,
            data_balance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=activation_date
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Get next queue position
        queue_position = subscription_service.get_next_queue_position(
            db, 
            linked_account.linked_customer_id or current_customer.customer_id, 
            linked_account.linked_phone_number
        )
        
        # Add to activation queue
        from app.models.models import SubscriptionActivationQueue
        queue_item = SubscriptionActivationQueue(
            subscription_id=subscription.subscription_id,
            customer_id=linked_account.linked_customer_id or current_customer.customer_id,
            phone_number=linked_account.linked_phone_number,
            expected_activation_date=activation_date,
            expected_expiry_date=expiry_date,
            queue_position=queue_position
        )
        
        db.add(queue_item)
        db.commit()
        
        message = f"Recharge successful for {linked_account.linked_phone_number}! Plan queued (position {queue_position}) and will activate when current plan expires."
    
    return RechargeLinkedResponse(
        transaction_id=transaction.transaction_id,
        linked_phone_number=linked_account.linked_phone_number,
        plan_name=plan.plan_name,
        final_amount=final_amount,
        message=message
    )