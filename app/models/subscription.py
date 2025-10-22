from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    subscription_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.plan_id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=False)
    is_topup = Column(Boolean, default=False)
    activation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    data_balance_gb = Column(DECIMAL(5, 2))
    daily_data_limit_gb = Column(DECIMAL(5, 2))
    daily_data_used_gb = Column(DECIMAL(5, 2), default=0.00)
    last_daily_reset = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    transaction = relationship("Transaction", back_populates="subscription")
    subscription_queues = relationship("SubscriptionActivationQueue", back_populates="subscription")
    active_topups = relationship("ActiveTopup", back_populates="base_subscription")

    __table_args__ = (
        CheckConstraint('daily_data_used_gb >= 0', name='chk_subscription_daily_data_used_positive'),
    )