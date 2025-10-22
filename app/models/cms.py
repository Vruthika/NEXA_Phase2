from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class HeaderContent(Base):
    __tablename__ = "header_content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    button_text = Column(String(100))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CarouselItem(Base):
    __tablename__ = "carousel_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    details = Column(Text)
    price_text = Column(String(100))
    plan_id = Column(Integer)
    image_url = Column(String(500))
    cta_text = Column(String(100))
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    image_url = Column(String(500))
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())