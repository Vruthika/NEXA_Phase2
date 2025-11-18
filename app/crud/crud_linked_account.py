from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional
from app.models.models import LinkedAccount, Customer
from app.schemas.linked_account import LinkedAccountCreate, LinkedAccountResponse

class CRUDLinkedAccount:
    def get_by_id(self, db: Session, linked_account_id: int):
        return db.query(LinkedAccount).filter(
            LinkedAccount.linked_account_id == linked_account_id
        ).first()
    
    def get_by_primary_customer(self, db: Session, primary_customer_id: int):
        """Get all linked accounts for a primary customer"""
        return db.query(LinkedAccount).filter(
            LinkedAccount.primary_customer_id == primary_customer_id
        ).all()
    
    def get_by_linked_customer(self, db: Session, linked_customer_id: int):
        """Get all linked accounts where customer is linked"""
        return db.query(LinkedAccount).filter(
            LinkedAccount.linked_customer_id == linked_customer_id
        ).all()
    
    def get_by_phone_number(self, db: Session, phone_number: str):
        """Get linked account by phone number"""
        return db.query(LinkedAccount).filter(
            LinkedAccount.linked_phone_number == phone_number
        ).first()
    
    def get_relationship(self, db: Session, primary_customer_id: int, linked_phone_number: str):
        """Check if relationship already exists"""
        return db.query(LinkedAccount).filter(
            and_(
                LinkedAccount.primary_customer_id == primary_customer_id,
                LinkedAccount.linked_phone_number == linked_phone_number
            )
        ).first()
    
    def create(self, db: Session, linked_account: LinkedAccountCreate):
        """Create a new linked account relationship"""
        
        # Check if relationship already exists
        existing = self.get_relationship(
            db, linked_account.primary_customer_id, linked_account.linked_phone_number
        )
        if existing:
            return None, "This phone number is already linked to your account"
        
        # Check if trying to link own number
        primary_customer = db.query(Customer).filter(
            Customer.customer_id == linked_account.primary_customer_id
        ).first()
        
        if primary_customer and primary_customer.phone_number == linked_account.linked_phone_number:
            return None, "Cannot link your own phone number"
        
        # Check if linked phone belongs to existing customer
        linked_customer = db.query(Customer).filter(
            Customer.phone_number == linked_account.linked_phone_number
        ).first()
        
        db_linked_account = LinkedAccount(
            primary_customer_id=linked_account.primary_customer_id,
            linked_phone_number=linked_account.linked_phone_number,
            linked_customer_id=linked_customer.customer_id if linked_customer else None
        )
        
        db.add(db_linked_account)
        db.commit()
        db.refresh(db_linked_account)
        return db_linked_account, None
    
    def delete(self, db: Session, linked_account_id: int, primary_customer_id: int):
        """Remove a linked account (only primary customer can remove)"""
        linked_account = db.query(LinkedAccount).filter(
            and_(
                LinkedAccount.linked_account_id == linked_account_id,
                LinkedAccount.primary_customer_id == primary_customer_id
            )
        ).first()
        
        if linked_account:
            db.delete(linked_account)
            db.commit()
            return True
        return False
    
    def get_linked_account_details(self, db: Session, linked_account_id: int):
        """Get detailed information about a linked account"""
        linked_account = self.get_by_id(db, linked_account_id)
        if not linked_account:
            return None
        
        # Get primary customer details
        primary_customer = db.query(Customer).filter(
            Customer.customer_id == linked_account.primary_customer_id
        ).first()
        
        # Get linked customer details if exists
        linked_customer = None
        if linked_account.linked_customer_id:
            linked_customer = db.query(Customer).filter(
                Customer.customer_id == linked_account.linked_customer_id
            ).first()
        
        return {
            "linked_account": linked_account,
            "primary_customer": primary_customer,
            "linked_customer": linked_customer
        }
    
    def get_all_linked_accounts_for_customer(self, db: Session, customer_id: int):
        """Get all linked accounts where customer is primary or linked"""
        # As primary customer
        as_primary = db.query(LinkedAccount).filter(
            LinkedAccount.primary_customer_id == customer_id
        ).all()
        
        # As linked customer
        as_linked = db.query(LinkedAccount).filter(
            LinkedAccount.linked_customer_id == customer_id
        ).all()
        
        return {
            "as_primary": as_primary,
            "as_linked": as_linked
        }

crud_linked_account = CRUDLinkedAccount()