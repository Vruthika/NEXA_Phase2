from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = "admins"
    
    admin_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    backups = relationship("Backup", back_populates="admin")
    restores = relationship("Restore", back_populates="admin")