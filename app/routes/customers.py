from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.customer import CustomerResponse, CustomerUpdate
from app.schemas.transaction import TransactionResponse
from app.schemas.subscription import SubscriptionResponse
from app.services.customer_service import CustomerService

router = APIRouter()

@router.get("/me", response_model=CustomerResponse)
async def get_current_customer_info(
    current_customer: CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    return customer_service.get_customer_by_id(current_customer.customer_id)

@router.put("/me", response_model=CustomerResponse)
async def update_customer_info(
    customer_data: CustomerUpdate,
    current_customer: CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    return customer_service.update_customer(current_customer.customer_id, customer_data)

@router.get("/me/transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    current_customer: CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    return customer_service.get_customer_transactions(current_customer.customer_id)

@router.get("/me/subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    current_customer: CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    return customer_service.get_customer_subscriptions(current_customer.customer_id)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_customer: CustomerResponse = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    customer_service.delete_customer(current_customer.customer_id)
    return None

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer_service = CustomerService(db)
    return customer_service.get_customer_by_id(customer_id)