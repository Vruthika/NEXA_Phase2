from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database import get_db
from app.config import settings
from app.services.customer_service import CustomerService
from app.services.admin_service import AdminService

security = HTTPBearer()

async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        customer_id: str = payload.get("sub")
        if customer_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    customer_service = CustomerService(db)
    customer = customer_service.get_customer_by_id(int(customer_id))
    if customer is None:
        raise credentials_exception
    return customer

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin_service = AdminService(db)
    admin = admin_service.get_admin_by_id(int(admin_id))
    if admin is None:
        raise credentials_exception
    return admin