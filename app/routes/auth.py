from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.crud import crud_referral
from app.database import get_db
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_token
)
from app.crud.crud_admin import crud_admin
from app.crud.crud_customer import crud_customer
from app.crud.crud_token import crud_token
from app.schemas.admin import AdminLogin
from app.schemas.customer import CustomerLogin, CustomerRegister, CustomerResponse
from app.schemas.token import Token, TokenRefresh, TokenResponse, LogoutResponse
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/analytics", tags=["Authentication"])
security = HTTPBearer()

# Admin Login with refresh token
@router.post("/admin/login", response_model=Token)
def admin_login(admin_login: AdminLogin, db: Session = Depends(get_db)):
    admin = crud_admin.authenticate(db, email=admin_login.email, password=admin_login.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(admin.admin_id)}, 
        expires_delta=access_token_expires,
        user_type="admin"
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": str(admin.admin_id), "user_type": "admin"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Customer Login with refresh token
@router.post("/customer/login", response_model=Token)
def customer_login(customer_login: CustomerLogin, db: Session = Depends(get_db)):
    customer = crud_customer.authenticate(db, phone_number=customer_login.phone_number, password=customer_login.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(customer.customer_id)}, 
        expires_delta=access_token_expires,
        user_type="customer"
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": str(customer.customer_id), "user_type": "customer"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Refresh token endpoint
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    # Verify refresh token and check if blacklisted
    if crud_token.is_token_blacklisted(db, token_refresh.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )
    
    payload = verify_token(token_refresh.refresh_token)
    if not payload:
        raise credentials_exception
    
    # Check if it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    user_type = payload.get("user_type")
    
    if not user_id or not user_type:
        raise credentials_exception
    
    # Verify user still exists
    if user_type == "admin":
        user = crud_admin.get_by_id(db, int(user_id))
    else:
        user = crud_customer.get_by_id(db, int(user_id))
    
    if not user:
        raise credentials_exception
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, 
        expires_delta=access_token_expires,
        user_type=user_type
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# LOGOUT ENDPOINT
@router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Simple logout - just blacklists the access token
    """
    access_token = credentials.credentials
    
    # Blacklist the access token
    success = crud_token.blacklist_token(db, access_token, "access", "logout")
    
    if success:
        return {"message": "Successfully logged out"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    
# Customer Registration
@router.post("/customer/register", response_model=CustomerResponse)
async def customer_register(customer_data: CustomerRegister, db: Session = Depends(get_db)):
    """
    Register a new customer account with optional referral code.
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
    
    # If referral code is provided in the customer_data, apply it
    if hasattr(customer_data, 'referral_code') and customer_data.referral_code:
        print(f"DEBUG: Applying referral code {customer_data.referral_code} for new customer {customer.customer_id}")
        
        referral_program, error = crud_referral.use_referral_code(
            db, 
            customer_data.referral_code, 
            customer.customer_id,  # Pass the actual customer ID
            customer.phone_number
        )
        
        # We don't fail registration if referral fails, just log it
        if error:
            print(f"Referral code application failed: {error}")
        else:
            print(f"Referral code applied successfully for new customer: {customer.phone_number}")
    
    return customer