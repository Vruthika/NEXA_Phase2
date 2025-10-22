from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, JSON, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PlanType(enum.Enum):
    PREPAID = "prepaid"
    POSTPAID = "postpaid"

class PlanStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Plan(Base):
    __tablename__ = "plans"
    
    plan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(Enum(PlanType), nullable=False)
    is_topup = Column(Boolean, default=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    validity_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    data_allowance_gb = Column(DECIMAL(5, 2))
    daily_data_limit_gb = Column(DECIMAL(5, 2))
    talktime_allowance_minutes = Column(Integer)
    sms_allowance = Column(Integer)
    benefits = Column(JSON)
    is_featured = Column(Boolean, default=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="plans")
    offers = relationship("Offer", back_populates="plan")
    transactions = relationship("Transaction", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")
    postpaid_activations = relationship("PostpaidActivation", back_populates="plan")
    active_topups = relationship("ActiveTopup", back_populates="topup_plan")

    __table_args__ = (
        CheckConstraint('price >= 0', name='chk_plan_price_positive'),
        CheckConstraint('validity_days > 0', name='chk_plan_validity_positive'),
    )