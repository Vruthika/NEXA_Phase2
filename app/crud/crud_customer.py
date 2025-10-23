from sqlalchemy.orm import Session
from app.models.models import Customer
from app.core.security import verify_password

class CRUDCustomer:
    def get_by_phone(self, db: Session, phone_number: str):
        return db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    def get_by_id(self, db: Session, customer_id: int):
        return db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def authenticate(self, db: Session, phone_number: str, password: str):
        customer = self.get_by_phone(db, phone_number)
        if not customer:
            return None
        if not verify_password(password, customer.password_hash):
            return None
        return customer

crud_customer = CRUDCustomer()