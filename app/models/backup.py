from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Backup(Base):
    __tablename__ = "backup"
    
    backup_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admins.admin_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # 'auto' or 'manual'
    date = Column(DateTime, default=func.now())
    data_list = Column(JSON, nullable=False)
    
    # Relationships
    admin = relationship("Admin", back_populates="backups")