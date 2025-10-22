from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class LinkedAccount(Base):
    __tablename__ = "linked_accounts"
    
    linked_account_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    primary_customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    linked_phone_number = Column(String(20), nullable=False)
    linked_customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    primary_customer = relationship("Customer", foreign_keys=[primary_customer_id], back_populates="linked_accounts_primary")
    linked_customer = relationship("Customer", foreign_keys=[linked_customer_id], back_populates="linked_accounts_linked")