# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.admin import AdminLogin, Token as AdminToken
from app.schemas.customer import CustomerLogin, Token as CustomerToken, CustomerRegister, CustomerResponse
from app.crud import crud_admin, crud_customer
from app.core.security import create_access_token
from app.config import settings

router = APIRouter(tags=["Authentication"])

# Admin Authentication
@router.post("/admin/login", response_model=AdminToken)
async def admin_login(login_data: AdminLogin, db: Session = Depends(get_db)):
    admin = crud_admin.authenticate(db, email=login_data.email, password=login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(admin.admin_id)}, 
        expires_delta=access_token_expires,
        user_type="admin"  # Add user type
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Customer Authentication
@router.post("/customer/login", response_model=CustomerToken)
async def customer_login(login_data: CustomerLogin, db: Session = Depends(get_db)):
    customer = crud_customer.authenticate(db, phone_number=login_data.phone_number, password=login_data.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(customer.customer_id)}, 
        expires_delta=access_token_expires,
        user_type="customer"  # Add user type
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Customer Registration
@router.post("/customer/register", response_model=CustomerResponse)
async def customer_register(customer_data: CustomerRegister, db: Session = Depends(get_db)):
    """
    Register a new customer account.
    """
    # Check if phone number already exists
    existing_customer = crud_customer.get_by_phone(db, customer_data.phone_number)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create new customer
    customer = crud_customer.create(db, customer_data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create customer account"
        )
    
    return customer