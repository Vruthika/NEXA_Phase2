from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Admin, Customer
from app.core.security import verify_token, is_token_blacklisted
from app.crud.crud_token import crud_token

security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin access required. Invalid admin token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    if crud_token.is_token_blacklisted(db, credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
        )
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise credentials_exception
    
    # Check if token has admin claim
    if payload.get("user_type") != "admin":
        raise credentials_exception
    
    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    
    try:
        admin_id_int = int(admin_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.admin_id == admin_id_int).first()
    if admin is None:
        raise credentials_exception
    
    return admin

def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Customer access required. Invalid customer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    if crud_token.is_token_blacklisted(db, credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
        )
    
    payload = verify_token(credentials.credentials)
    if not payload:
        raise credentials_exception
    
    # Check if token has customer claim
    if payload.get("user_type") != "customer":
        raise credentials_exception
    
    customer_id: str = payload.get("sub")
    if customer_id is None:
        raise credentials_exception
    
    try:
        customer_id_int = int(customer_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id_int).first()
    if customer is None:
        raise credentials_exception
    
    return customer