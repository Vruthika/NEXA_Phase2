from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.customer_crud import CustomerCRUD
from app.schemas.customer import CustomerCreate, CustomerLogin
from app.utils.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_crud = CustomerCRUD(db)
    
    def register_customer(self, customer_data: CustomerCreate):
        # Check if phone number already exists
        existing_customer = self.customer_crud.get_by_phone(customer_data.phone_number)
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(customer_data.password)
        
        # Create customer
        customer_dict = customer_data.dict()
        customer_dict['password_hash'] = hashed_password
        del customer_dict['password']
        
        customer = self.customer_crud.create(customer_dict)
        return customer
    
    def authenticate_customer(self, login_data: CustomerLogin):
        customer = self.customer_crud.get_by_phone(login_data.phone_number)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not verify_password(login_data.password, customer.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate access token
        access_token = create_access_token(data={"sub": str(customer.customer_id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "customer_id": customer.customer_id
        }
    
    def get_current_customer(self, customer_id: int):
        return self.customer_crud.get_by_id(customer_id)