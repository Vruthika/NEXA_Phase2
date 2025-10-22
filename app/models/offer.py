from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Offer(Base):
    __tablename__ = "offers"
    
    offer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("plans.plan_id"), nullable=False)
    discounted_price = Column(DECIMAL(10, 2), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    plan = relationship("Plan", back_populates="offers")
    transactions = relationship("Transaction", back_populates="offer")

    __table_args__ = (
        CheckConstraint('discounted_price >= 0', name='chk_offer_discounted_price_positive'),
    )