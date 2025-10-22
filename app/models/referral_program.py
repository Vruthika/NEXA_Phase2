from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ReferralStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"

class ReferralProgram(Base):
    __tablename__ = "referral_program"
    
    referral_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    referrer_customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    referee_phone_number = Column(String(20), nullable=False)
    referral_code = Column(String(20), unique=True, nullable=False)
    status = Column(Enum(ReferralStatus), default=ReferralStatus.PENDING)
    referee_customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    referrer_customer = relationship("Customer", foreign_keys=[referrer_customer_id], back_populates="referral_programs_referrer")
    referee_customer = relationship("Customer", foreign_keys=[referee_customer_id], back_populates="referral_programs_referee")
    referral_discounts = relationship("ReferralDiscount", back_populates="referral_program")
    usage_logs = relationship("ReferralUsageLog", back_populates="referral_program")

    __table_args__ = (
        CheckConstraint('max_uses > 0', name='chk_referral_max_uses_positive'),
        CheckConstraint('current_uses <= max_uses', name='chk_referral_current_uses_limit'),
    )