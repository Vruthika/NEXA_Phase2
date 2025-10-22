from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.services.subscription_service import SubscriptionService

router = APIRouter()

@router.get("/my-queue")
async def get_my_queue(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    # This would require a method to get queue entries by customer
    # For now, return a placeholder response
    return {"message": "Queue functionality will be implemented"}

@router.post("/process/{phone_number}")
async def process_queue(
    phone_number: str,
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    result = subscription_service.process_queued_subscriptions(phone_number)
    
    if result:
        return {
            "message": "Queue processed successfully",
            "activated_subscription_id": result.subscription_id
        }
    else:
        return {
            "message": "No queued subscriptions to process"
        }