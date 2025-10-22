from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.utils.security import get_password_hash
from datetime import datetime

class CustomerCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, customer_id: int) -> Customer:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def get_by_phone(self, phone_number: str) -> Customer:
        return self.db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Customer).filter(Customer.deleted_at.is_(None)).offset(skip).limit(limit).all()
    
    def create(self, customer_data: dict) -> Customer:
        customer = Customer(**customer_data)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    def update(self, customer_id: int, customer_data: dict) -> Customer:
        customer = self.get_by_id(customer_id)
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    def soft_delete(self, customer_id: int) -> Customer:
        customer = self.get_by_id(customer_id)
        if customer:
            customer.deleted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    def update_inactivity_status(self, customer_id: int, days_inactive: int) -> Customer:
        customer = self.get_by_id(customer_id)
        if customer:
            customer.days_inactive = days_inactive
            customer.inactivity_status_updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    def update_last_active_plan_date(self, customer_id: int) -> Customer:
        customer = self.get_by_id(customer_id)
        if customer:
            customer.last_active_plan_date = datetime.utcnow()
            self.db.commit()
            self.db.refresh(customer)
        return customer