from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    plans = relationship("Plan", back_populates="category")