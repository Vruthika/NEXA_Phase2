from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.linked_account import LinkedAccountCreate, LinkedAccountResponse
from app.services.linked_account_service import LinkedAccountService

router = APIRouter()

@router.post("/", response_model=LinkedAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_linked_account(
    linked_account_data: LinkedAccountCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    linked_account_service = LinkedAccountService(db)
    return linked_account_service.create_linked_account(
        current_customer.customer_id,
        linked_account_data
    )

@router.get("/my-linked-accounts", response_model=List[LinkedAccountResponse])
async def get_my_linked_accounts(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    linked_account_service = LinkedAccountService(db)
    return linked_account_service.get_linked_accounts_by_primary(current_customer.customer_id)

@router.get("/linked-to-me", response_model=List[LinkedAccountResponse])
async def get_accounts_linked_to_me(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    linked_account_service = LinkedAccountService(db)
    return linked_account_service.get_linked_accounts_by_linked(current_customer.customer_id)

@router.delete("/{linked_account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_linked_account(
    linked_account_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    linked_account_service = LinkedAccountService(db)
    linked_account_service.delete_linked_account(linked_account_id, current_customer.customer_id)
    return None