from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.admin import AdminLogin, Token as AdminToken
from app.schemas.customer import CustomerLogin, Token as CustomerToken
from app.crud import crud_admin, crud_customer
from app.core.security import create_access_token
from app.config import settings

router = APIRouter(tags=["authentication"])

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
        data={"sub": str(admin.admin_id)}, expires_delta=access_token_expires
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
        data={"sub": str(customer.customer_id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}