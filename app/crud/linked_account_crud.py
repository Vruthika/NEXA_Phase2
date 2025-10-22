from sqlalchemy.orm import Session
from app.models.linked_account import LinkedAccount

class LinkedAccountCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, linked_account_id: int) -> LinkedAccount:
        return self.db.query(LinkedAccount).filter(LinkedAccount.linked_account_id == linked_account_id).first()
    
    def get_by_primary_customer(self, primary_customer_id: int):
        return self.db.query(LinkedAccount).filter(LinkedAccount.primary_customer_id == primary_customer_id).all()
    
    def get_by_linked_customer(self, linked_customer_id: int):
        return self.db.query(LinkedAccount).filter(LinkedAccount.linked_customer_id == linked_customer_id).all()
    
    def get_by_primary_and_phone(self, primary_customer_id: int, linked_phone_number: str):
        return self.db.query(LinkedAccount).filter(
            LinkedAccount.primary_customer_id == primary_customer_id,
            LinkedAccount.linked_phone_number == linked_phone_number
        ).first()
    
    def create(self, linked_account_data: dict) -> LinkedAccount:
        linked_account = LinkedAccount(**linked_account_data)
        self.db.add(linked_account)
        self.db.commit()
        self.db.refresh(linked_account)
        return linked_account
    
    def delete(self, linked_account_id: int) -> bool:
        linked_account = self.get_by_id(linked_account_id)
        if linked_account:
            self.db.delete(linked_account)
            self.db.commit()
            return True
        return False