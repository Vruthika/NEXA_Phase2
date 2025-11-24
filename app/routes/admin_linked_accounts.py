from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Admin, LinkedAccount, Customer
from app.core.auth import get_current_admin
from app.schemas.linked_account import LinkedAccountResponse
from app.crud.crud_linked_account import crud_linked_account

router = APIRouter(prefix="/linked-accounts", tags=["Admin - Linked Accounts"])

@router.get("/", response_model=List[LinkedAccountResponse])
async def get_all_linked_accounts(
    primary_customer_id: Optional[int] = Query(None, description="Filter by primary customer"),
    linked_phone: Optional[str] = Query(None, description="Filter by linked phone number"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all linked account relationships in the system.
    """
    query = db.query(LinkedAccount)
    
    # Apply filters
    if primary_customer_id:
        query = query.filter(LinkedAccount.primary_customer_id == primary_customer_id)
    
    if linked_phone:
        query = query.filter(LinkedAccount.linked_phone_number.ilike(f"%{linked_phone}%"))
    
    linked_accounts = query.all()
    
    response_accounts = []
    for account in linked_accounts:
        # Get customer details
        primary_customer = db.query(Customer).filter(
            Customer.customer_id == account.primary_customer_id
        ).first()
        
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
            primary_customer_name=primary_customer.full_name if primary_customer else "Unknown",
            linked_customer_name=linked_customer.full_name if linked_customer else None,
            is_registered_user=account.linked_customer_id is not None
        ))
    
    return response_accounts

@router.get("/customer/{customer_id}")
async def get_customer_linked_relationships(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all linked account relationships for a specific customer
    (both as primary and as linked customer).
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    relationships = crud_linked_account.get_all_linked_accounts_for_customer(db, customer_id)
    
    # Format response
    as_primary = []
    for account in relationships["as_primary"]:
        linked_customer = None
        if account.linked_customer_id:
            linked_customer = db.query(Customer).filter(
                Customer.customer_id == account.linked_customer_id
            ).first()
        
        as_primary.append({
            "linked_account_id": account.linked_account_id,
            "linked_phone_number": account.linked_phone_number,
            "linked_customer_name": linked_customer.full_name if linked_customer else None,
            "is_registered_user": account.linked_customer_id is not None,
            "created_at": account.created_at
        })
    
    as_linked = []
    for account in relationships["as_linked"]:
        primary_customer = db.query(Customer).filter(
            Customer.customer_id == account.primary_customer_id
        ).first()
        
        as_linked.append({
            "linked_account_id": account.linked_account_id,
            "primary_customer_name": primary_customer.full_name if primary_customer else "Unknown",
            "primary_phone_number": primary_customer.phone_number if primary_customer else "Unknown",
            "created_at": account.created_at
        })
    
    return {
        "customer": {
            "customer_id": customer.customer_id,
            "full_name": customer.full_name,
            "phone_number": customer.phone_number
        },
        "as_primary_owner": as_primary,
        "as_linked_account": as_linked
    }

@router.delete("/{linked_account_id}")
async def admin_remove_linked_account(
    linked_account_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Remove any linked account relationship.
    """
    linked_account = crud_linked_account.get_by_id(db, linked_account_id)
    if not linked_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked account not found"
        )
    
    db.delete(linked_account)
    db.commit()
    
    return {"message": "Linked account relationship removed successfully by admin"}