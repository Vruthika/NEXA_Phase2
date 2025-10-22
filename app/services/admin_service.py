from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.admin_crud import AdminCRUD
from app.schemas.admin import AdminCreate, AdminUpdate
from app.utils.security import get_password_hash, verify_password, create_access_token

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.admin_crud = AdminCRUD(db)
    
    def authenticate_admin(self, email: str, password: str):
        admin = self.admin_crud.get_by_email(email)
        if not admin:
            return None
        
        if not verify_password(password, admin.password_hash):
            return None
        
        return admin
    
    def get_admin_by_id(self, admin_id: int):
        admin = self.admin_crud.get_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin
    
    def create_admin(self, admin_data: AdminCreate):
        # Check if email already exists
        existing_admin = self.admin_crud.get_by_email(admin_data.email)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if phone number already exists
        existing_phone_admin = self.admin_crud.get_by_phone(admin_data.phone_number)
        if existing_phone_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(admin_data.password)
        
        # Create admin
        admin_dict = admin_data.dict()
        admin_dict['password_hash'] = hashed_password
        del admin_dict['password']
        
        return self.admin_crud.create(admin_dict)
    
    def update_admin(self, admin_id: int, admin_data: AdminUpdate):
        admin = self.get_admin_by_id(admin_id)
        return self.admin_crud.update(admin_id, admin_data.dict(exclude_unset=True))
    
    def get_all_admins(self, skip: int = 0, limit: int = 100):
        return self.admin_crud.get_all(skip, limit)