from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Customer, Transaction, Subscription, SubscriptionActivationQueue, AccountStatus
from app.schemas.customer import CustomerFilter, CustomerUpdate, CustomerRegister
from app.core.security import get_password_hash, verify_password

class CRUDCustomer:
    def get_by_phone(self, db: Session, phone_number: str):
        return db.query(Customer).filter(Customer.phone_number == phone_number).first()
    
    def get_by_id(self, db: Session, customer_id: int):
        return db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def authenticate(self, db: Session, phone_number: str, password: str):
        """Authenticate a customer by phone number and password"""
        customer = self.get_by_phone(db, phone_number)
        if not customer:
            return None
        if not verify_password(password, customer.password_hash):
            return None
        return customer
    
    def create(self, db: Session, customer: CustomerRegister):
        # Check if phone number already exists
        existing_customer = self.get_by_phone(db, customer.phone_number)
        if existing_customer:
            return None
        
        hashed_password = get_password_hash(customer.password)
        db_customer = Customer(
            phone_number=customer.phone_number,
            password_hash=hashed_password,
            full_name=customer.full_name,
            profile_picture_url=customer.profile_picture_url,
            account_status=AccountStatus.active
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def update_last_active_plan_date(self, db: Session, customer_id: int):
        """Update the customer's last_active_plan_date based on active subscriptions"""
        customer = self.get_by_id(db, customer_id)
        if customer:
            # Find the most recent active subscription
            latest_subscription = db.query(Subscription).filter(
                Subscription.customer_id == customer_id,
                Subscription.expiry_date > datetime.utcnow()
            ).order_by(Subscription.activation_date.desc()).first()
            
            if latest_subscription:
                customer.last_active_plan_date = latest_subscription.activation_date
                customer.days_inactive = 0
            else:
                # If no active subscription, calculate days inactive
                if customer.last_active_plan_date:
                    days_inactive = (datetime.utcnow() - customer.last_active_plan_date).days
                    customer.days_inactive = max(0, days_inactive)
                else:
                    customer.days_inactive = 0
            
            customer.inactivity_status_updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
        return customer
    
    def get_all(
        self, 
        db: Session, 
        filter: CustomerFilter,
        skip: int = 0, 
        limit: int = 100
    ):
        query = db.query(Customer).filter(Customer.deleted_at.is_(None))
        
        # Apply filters
        if filter.phone_number:
            query = query.filter(Customer.phone_number.ilike(f"%{filter.phone_number}%"))
        
        if filter.full_name:
            query = query.filter(Customer.full_name.ilike(f"%{filter.full_name}%"))
        
        if filter.account_status:
            query = query.filter(Customer.account_status == filter.account_status)
        
        return query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_customer_details(self, db: Session, customer_id: int):
        """Get customer with additional statistics"""
        customer = self.get_by_id(db, customer_id)
        if not customer:
            return None
        
        # Get transaction statistics
        transaction_stats = db.query(
            func.count(Transaction.transaction_id).label('total_transactions'),
            func.sum(Transaction.final_amount).label('total_spent')
        ).filter(
            Transaction.customer_id == customer_id,
            Transaction.payment_status == 'success'
        ).first()
        
        # Get subscription statistics
        active_subscriptions = db.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.expiry_date > datetime.utcnow()
        ).count()
        
        queued_subscriptions = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.processed_at.is_(None)
        ).count()
        
        # Get referral code if exists
        from app.models.models import ReferralProgram
        referral_code = db.query(ReferralProgram.referral_code).filter(
            ReferralProgram.referrer_customer_id == customer_id,
            ReferralProgram.is_active == True
        ).first()
        
        return {
            'customer': customer,
            'total_transactions': transaction_stats.total_transactions or 0,
            'total_spent': float(transaction_stats.total_spent or 0),
            'active_subscriptions': active_subscriptions,
            'queued_subscriptions': queued_subscriptions,
            'referral_code': referral_code[0] if referral_code else None
        }
    
    def update_customer(self, db: Session, customer_id: int, customer_update: CustomerUpdate):
        customer = self.get_by_id(db, customer_id)
        if customer:
            update_data = customer_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(customer, field, value)
            customer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
        return customer
    
    def deactivate_account(self, db: Session, customer_id: int):
        """Deactivate customer account"""
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.account_status = AccountStatus.inactive
            customer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
        return customer
    
    def activate_account(self, db: Session, customer_id: int):
        """Activate customer account"""
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.account_status = AccountStatus.active
            customer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
        return customer
    
    def suspend_account(self, db: Session, customer_id: int):
        """Suspend customer account"""
        customer = self.get_by_id(db, customer_id)
        if customer:
            customer.account_status = AccountStatus.suspended
            customer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(customer)
        return customer
    
    def get_customer_transactions(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        """Get transaction history for a customer"""
        return db.query(Transaction).filter(
            Transaction.customer_id == customer_id
        ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    def get_customer_subscriptions(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        """Get subscription history for a customer"""
        return db.query(Subscription).filter(
            Subscription.customer_id == customer_id
        ).options(
            joinedload(Subscription.plan)
        ).order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_customer_queued_subscriptions(self, db: Session, customer_id: int):
        """Get queued subscriptions for a customer"""
        return db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.processed_at.is_(None)
        ).options(
            joinedload(SubscriptionActivationQueue.subscription).joinedload(Subscription.plan)
        ).order_by(SubscriptionActivationQueue.queue_position).all()
    
    def get_customer_stats(self, db: Session):
        """Get overall customer statistics"""
        total_customers = db.query(Customer).filter(Customer.deleted_at.is_(None)).count()
        active_customers = db.query(Customer).filter(
            Customer.account_status == AccountStatus.active,
            Customer.deleted_at.is_(None)
        ).count()
        inactive_customers = db.query(Customer).filter(
            Customer.account_status == AccountStatus.inactive,
            Customer.deleted_at.is_(None)
        ).count()
        suspended_customers = db.query(Customer).filter(
            Customer.account_status == AccountStatus.suspended,
            Customer.deleted_at.is_(None)
        ).count()
        
        # New customers today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_customers_today = db.query(Customer).filter(
            Customer.created_at >= today_start,
            Customer.deleted_at.is_(None)
        ).count()
        
        # New customers this week
        week_start = today_start - timedelta(days=today_start.weekday())
        new_customers_this_week = db.query(Customer).filter(
            Customer.created_at >= week_start,
            Customer.deleted_at.is_(None)
        ).count()
        
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'inactive_customers': inactive_customers,
            'suspended_customers': suspended_customers,
            'new_customers_today': new_customers_today,
            'new_customers_this_week': new_customers_this_week
        }
    
    def search_customers(self, db: Session, search_term: str, skip: int = 0, limit: int = 50):
        """Search customers by phone number or name"""
        return db.query(Customer).filter(
            Customer.deleted_at.is_(None),
            or_(
                Customer.phone_number.ilike(f"%{search_term}%"),
                Customer.full_name.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()

crud_customer = CRUDCustomer()