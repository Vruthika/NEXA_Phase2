from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    full_name = Column(String(255), nullable=False)
    profile_picture_url = Column(String(300))
    last_active_plan_date = Column(DateTime)
    days_inactive = Column(Integer, default=0)
    inactivity_status_updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    subscription_queues = relationship("SubscriptionActivationQueue", back_populates="customer")
    active_topups = relationship("ActiveTopup", back_populates="customer")
    linked_accounts_primary = relationship("LinkedAccount", foreign_keys="LinkedAccount.primary_customer_id", back_populates="primary_customer")
    linked_accounts_linked = relationship("LinkedAccount", foreign_keys="LinkedAccount.linked_customer_id", back_populates="linked_customer")
    postpaid_activations = relationship("PostpaidActivation", back_populates="customer")
    referral_programs_referrer = relationship("ReferralProgram", foreign_keys="ReferralProgram.referrer_customer_id", back_populates="referrer_customer")
    referral_programs_referee = relationship("ReferralProgram", foreign_keys="ReferralProgram.referee_customer_id", back_populates="referee_customer")
    referral_discounts = relationship("ReferralDiscount", back_populates="customer")
    referral_usage_logs = relationship("ReferralUsageLog", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")