from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TopupStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    EXPIRED = "expired"

class ActiveTopup(Base):
    __tablename__ = "active_topups"
    
    topup_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    base_subscription_id = Column(Integer, ForeignKey("subscriptions.subscription_id"), nullable=False)
    topup_plan_id = Column(Integer, ForeignKey("plans.plan_id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=False)
    topup_data_gb = Column(DECIMAL(5, 2), nullable=False)
    data_remaining_gb = Column(DECIMAL(5, 2), nullable=False)
    activation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(Enum(TopupStatus), default=TopupStatus.PENDING)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="active_topups")
    base_subscription = relationship("Subscription", back_populates="active_topups")
    topup_plan = relationship("Plan", back_populates="active_topups")
    transaction = relationship("Transaction", back_populates="active_topup")

    __table_args__ = (
        CheckConstraint('topup_data_gb > 0', name='chk_topup_data_positive'),
        CheckConstraint('data_remaining_gb >= 0', name='chk_topup_data_remaining_positive'),
    )