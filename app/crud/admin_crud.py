from sqlalchemy.orm import Session
from app.models.admin import Admin

class AdminCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, admin_id: int) -> Admin:
        return self.db.query(Admin).filter(Admin.admin_id == admin_id).first()
    
    def get_by_email(self, email: str) -> Admin:
        return self.db.query(Admin).filter(Admin.email == email).first()
    
    def get_by_phone(self, phone_number: str) -> Admin:
        return self.db.query(Admin).filter(Admin.phone_number == phone_number).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Admin).offset(skip).limit(limit).all()
    
    def create(self, admin_data: dict) -> Admin:
        admin = Admin(**admin_data)
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin
    
    def update(self, admin_id: int, admin_data: dict) -> Admin:
        admin = self.get_by_id(admin_id)
        if admin:
            for key, value in admin_data.items():
                setattr(admin, key, value)
            self.db.commit()
            self.db.refresh(admin)
        return admin
    
    def delete(self, admin_id: int) -> bool:
        admin = self.get_by_id(admin_id)
        if admin:
            self.db.delete(admin)
            self.db.commit()
            return True
        return False