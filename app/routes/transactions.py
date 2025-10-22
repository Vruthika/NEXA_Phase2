from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter()

@router.post("/recharge", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_recharge(
    transaction_data: TransactionCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService(db)
    return transaction_service.create_transaction(current_customer.customer_id, transaction_data)

@router.get("/my-transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService(db)
    return transaction_service.get_customer_transactions(current_customer.customer_id)

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    transaction_service = TransactionService(db)
    transaction = transaction_service.get_transaction_by_id(transaction_id)
    
    # Ensure the transaction belongs to the current customer
    if transaction.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transaction"
        )
    
    return transaction