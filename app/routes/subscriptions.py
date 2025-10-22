from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate
from app.services.subscription_service import SubscriptionService

router = APIRouter()

@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.create_subscription(current_customer.customer_id, subscription_data)

@router.get("/my-subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_customer_subscriptions(current_customer.customer_id)

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription_by_id(
    subscription_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription_by_id(subscription_id)
    
    # Verify subscription belongs to current customer
    if subscription.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this subscription"
        )
    
    return subscription

@router.post("/{subscription_id}/queue", response_model=dict)
async def queue_subscription_activation(
    subscription_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription_by_id(subscription_id)
    
    queue_entry = subscription_service.queue_subscription_activation(
        current_customer.customer_id,
        subscription_id,
        subscription.phone_number
    )
    
    return {
        "message": "Subscription queued for activation",
        "queue_id": queue_entry.queue_id,
        "queue_position": queue_entry.queue_position,
        "expected_activation_date": queue_entry.expected_activation_date.isoformat()
    }

@router.post("/{subscription_id}/update-usage")
async def update_subscription_usage(
    subscription_id: int,
    data_used_gb: float,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription_by_id(subscription_id)
    
    # Verify subscription belongs to current customer
    if subscription.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this subscription"
        )
    
    updated_subscription = subscription_service.update_data_usage(subscription_id, data_used_gb)
    
    return {
        "message": "Data usage updated successfully",
        "subscription_id": subscription_id,
        "data_used_gb": data_used_gb,
        "remaining_balance_gb": float(updated_subscription.data_balance_gb) if updated_subscription.data_balance_gb else None,
        "daily_used_gb": float(updated_subscription.daily_data_used_gb)
    }

@router.post("/{subscription_id}/reset-daily-usage", response_model=SubscriptionResponse)
async def reset_daily_usage(
    subscription_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription_by_id(subscription_id)
    
    # Verify subscription belongs to current customer
    if subscription.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reset this subscription"
        )
    
    return subscription_service.reset_daily_usage(subscription_id)