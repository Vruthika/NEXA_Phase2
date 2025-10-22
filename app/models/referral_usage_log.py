from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ReferralUsageLog(Base):
    __tablename__ = "referral_usage_log"
    
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    referral_id = Column(Integer, ForeignKey("referral_program.referral_id"), nullable=False)
    used_by_phone = Column(String(20), nullable=False)
    used_by_customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    used_at = Column(DateTime, default=func.now())
    
    # Relationships
    referral_program = relationship("ReferralProgram", back_populates="usage_logs")
    customer = relationship("Customer", back_populates="referral_usage_logs")