from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from datetime import datetime, timedelta

class TransactionCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, transaction_id: int) -> Transaction:
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(Transaction).filter(Transaction.customer_id == customer_id).all()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Transaction).offset(skip).limit(limit).all()
    
    def create(self, transaction_data: dict) -> Transaction:
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update_status(self, transaction_id: int, status: str) -> Transaction:
        transaction = self.get_by_id(transaction_id)
        if transaction:
            transaction.payment_status = status
            self.db.commit()
            self.db.refresh(transaction)
        return transaction
    
    def get_recent_transactions(self, days: int = 7):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(Transaction).filter(Transaction.transaction_date >= cutoff_date).all()