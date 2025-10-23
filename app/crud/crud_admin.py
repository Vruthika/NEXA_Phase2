from sqlalchemy.orm import Session
from app.models.models import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash, verify_password

class CRUDAdmin:
    def get_by_email(self, db: Session, email: str):
        return db.query(Admin).filter(Admin.email == email).first()
    
    def get_by_id(self, db: Session, admin_id: int):
        return db.query(Admin).filter(Admin.admin_id == admin_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Admin).offset(skip).limit(limit).all()
    
    def create(self, db: Session, admin: AdminCreate):
        hashed_password = get_password_hash(admin.password)
        db_admin = Admin(
            name=admin.name,
            phone_number=admin.phone_number,
            email=admin.email,
            password_hash=hashed_password
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin
    
    def update(self, db: Session, admin_id: int, admin_update: AdminUpdate):
        db_admin = self.get_by_id(db, admin_id)
        if db_admin:
            update_data = admin_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_admin, field, value)
            db.commit()
            db.refresh(db_admin)
        return db_admin
    
    def change_password(self, db: Session, admin_id: int, new_password: str):
        db_admin = self.get_by_id(db, admin_id)
        if db_admin:
            db_admin.password_hash = get_password_hash(new_password)
            db.commit()
            db.refresh(db_admin)
        return db_admin
    
    def authenticate(self, db: Session, email: str, password: str):
        admin = self.get_by_email(db, email)
        if not admin:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin

crud_admin = CRUDAdmin()