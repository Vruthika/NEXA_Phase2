from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ReferralDiscount(Base):
    __tablename__ = "referral_discounts"
    
    discount_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    referral_id = Column(Integer, ForeignKey("referral_program.referral_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=10.00)
    is_used = Column(Boolean, default=False)
    valid_until = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    used_at = Column(DateTime)
    
    # Relationships
    referral_program = relationship("ReferralProgram", back_populates="referral_discounts")
    customer = relationship("Customer", back_populates="referral_discounts")

    __table_args__ = (
        CheckConstraint('discount_percentage > 0 AND discount_percentage <= 100', name='chk_discount_percentage_range'),
    )