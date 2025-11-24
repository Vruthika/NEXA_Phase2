from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Transaction, Customer, Plan, Offer
from app.schemas.transaction import TransactionFilter

class CRUDTransaction:
    def get(self, db: Session, transaction_id: int):
        return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_all(
        self, 
        db: Session, 
        filter: TransactionFilter,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(Transaction)
        
        # Apply filters
        if filter.customer_id:
            query = query.filter(Transaction.customer_id == filter.customer_id)
        
        if filter.customer_phone:
            # Join with customers table to filter by phone
            query = query.join(Customer).filter(Customer.phone_number.ilike(f"%{filter.customer_phone}%"))
        
        if filter.plan_id:
            query = query.filter(Transaction.plan_id == filter.plan_id)
        
        if filter.transaction_type:
            query = query.filter(Transaction.transaction_type == filter.transaction_type)
        
        if filter.payment_status:
            query = query.filter(Transaction.payment_status == filter.payment_status)
        
        if filter.payment_method:
            query = query.filter(Transaction.payment_method == filter.payment_method)
        
        if filter.date_from:
            query = query.filter(Transaction.transaction_date >= filter.date_from)
        
        if filter.date_to:
            # Add 1 day to include the entire end date
            end_date = filter.date_to + timedelta(days=1)
            query = query.filter(Transaction.transaction_date < end_date)
        
        return query.offset(skip).limit(limit).all()
    
    def get_with_details(self, db: Session, transaction_id: int):
        return db.query(
            Transaction,
            Customer.full_name,
            Customer.phone_number,
            Plan.plan_name,
            Offer.offer_name
        ).join(
            Customer, Transaction.customer_id == Customer.customer_id
        ).join(
            Plan, Transaction.plan_id == Plan.plan_id
        ).outerjoin(
            Offer, Transaction.offer_id == Offer.offer_id
        ).filter(
            Transaction.transaction_id == transaction_id
        ).first()
    
    def get_all_with_details(self, db: Session, filter: TransactionFilter, skip: int = 0, limit: int = 100):
        query = db.query(
            Transaction,
            Customer.full_name,
            Customer.phone_number,
            Plan.plan_name,
            Offer.offer_name
        ).join(
            Customer, Transaction.customer_id == Customer.customer_id
        ).join(
            Plan, Transaction.plan_id == Plan.plan_id
        ).outerjoin(
            Offer, Transaction.offer_id == Offer.offer_id
        )
        
        # Apply filters
        if filter.customer_id:
            query = query.filter(Transaction.customer_id == filter.customer_id)
        
        if filter.customer_phone:
            query = query.filter(Customer.phone_number.ilike(f"%{filter.customer_phone}%"))
        
        if filter.plan_id:
            query = query.filter(Transaction.plan_id == filter.plan_id)
        
        if filter.transaction_type:
            query = query.filter(Transaction.transaction_type == filter.transaction_type)
        
        if filter.payment_status:
            query = query.filter(Transaction.payment_status == filter.payment_status)
        
        if filter.payment_method:
            query = query.filter(Transaction.payment_method == filter.payment_method)
        
        if filter.date_from:
            query = query.filter(Transaction.transaction_date >= filter.date_from)
        
        if filter.date_to:
            end_date = filter.date_to + timedelta(days=1)
            query = query.filter(Transaction.transaction_date < end_date)
        
        return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    def get_total_count(self, db: Session, filter: TransactionFilter):
        query = db.query(Transaction)
        
        # Apply filters 
        if filter.customer_id:
            query = query.filter(Transaction.customer_id == filter.customer_id)
        
        if filter.customer_phone:
            query = query.join(Customer).filter(Customer.phone_number.ilike(f"%{filter.customer_phone}%"))
        
        if filter.plan_id:
            query = query.filter(Transaction.plan_id == filter.plan_id)
        
        if filter.transaction_type:
            query = query.filter(Transaction.transaction_type == filter.transaction_type)
        
        if filter.payment_status:
            query = query.filter(Transaction.payment_status == filter.payment_status)
        
        if filter.payment_method:
            query = query.filter(Transaction.payment_method == filter.payment_method)
        
        if filter.date_from:
            query = query.filter(Transaction.transaction_date >= filter.date_from)
        
        if filter.date_to:
            end_date = filter.date_to + timedelta(days=1)
            query = query.filter(Transaction.transaction_date < end_date)
        
        return query.count()
    
    def get_revenue_stats(self, db: Session, days: int = 30):
        """Get revenue statistics for the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        total_revenue = db.query(
            db.func.sum(Transaction.final_amount)
        ).filter(
            Transaction.payment_status == "success",
            Transaction.transaction_date >= since_date
        ).scalar() or 0.0
        
        successful_transactions = db.query(Transaction).filter(
            Transaction.payment_status == "success",
            Transaction.transaction_date >= since_date
        ).count()
        
        failed_transactions = db.query(Transaction).filter(
            Transaction.payment_status == "failed",
            Transaction.transaction_date >= since_date
        ).count()
        
        return {
            "total_revenue": float(total_revenue),
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "period_days": days
        }

crud_transaction = CRUDTransaction()