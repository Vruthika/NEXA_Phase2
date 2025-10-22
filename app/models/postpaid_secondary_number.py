from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class PostpaidSecondaryNumber(Base):
    __tablename__ = "postpaid_secondary_numbers"
    
    secondary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activation_id = Column(Integer, ForeignKey("postpaid_activations.activation_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    added_date = Column(DateTime, default=func.now())
    
    # Relationships
    activation = relationship("PostpaidActivation", back_populates="secondary_numbers")
    customer = relationship("Customer")