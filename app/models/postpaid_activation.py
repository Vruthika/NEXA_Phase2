from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PostpaidStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class PostpaidActivation(Base):
    __tablename__ = "postpaid_activations"
    
    activation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.plan_id"), nullable=False)
    primary_number = Column(String(20), nullable=False)
    billing_cycle_start = Column(DateTime, nullable=False)
    billing_cycle_end = Column(DateTime, nullable=False)
    base_data_allowance_gb = Column(DECIMAL(5, 2), nullable=False)
    current_data_balance_gb = Column(DECIMAL(5, 2), nullable=False)
    data_used_gb = Column(DECIMAL(5, 2), default=0.00)
    base_amount = Column(DECIMAL(10, 2), nullable=False)
    total_amount_due = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(PostpaidStatus), default=PostpaidStatus.ACTIVE)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="postpaid_activations")
    plan = relationship("Plan", back_populates="postpaid_activations")
    secondary_numbers = relationship("PostpaidSecondaryNumber", back_populates="activation")
    data_addons = relationship("PostpaidDataAddon", back_populates="activation")

    __table_args__ = (
        CheckConstraint('current_data_balance_gb >= 0', name='chk_postpaid_data_balance_positive'),
        CheckConstraint('data_used_gb >= 0', name='chk_postpaid_data_used_positive'),
        CheckConstraint('base_amount >= 0', name='chk_postpaid_base_amount_positive'),
        CheckConstraint('total_amount_due >= 0', name='chk_postpaid_total_amount_positive'),
    )