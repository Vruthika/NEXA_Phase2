from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AddonStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    FULLY_USED = "fully_used"

class PostpaidDataAddon(Base):
    __tablename__ = "postpaid_data_addons"
    
    addon_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activation_id = Column(Integer, ForeignKey("postpaid_activations.activation_id"), nullable=False)
    addon_name = Column(String(100), nullable=False)
    data_amount_gb = Column(DECIMAL(5, 2), nullable=False)
    addon_price = Column(DECIMAL(10, 2), nullable=False)
    purchased_date = Column(DateTime, default=func.now())
    valid_until = Column(DateTime, nullable=False)
    status = Column(Enum(AddonStatus), default=AddonStatus.ACTIVE)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    activation = relationship("PostpaidActivation", back_populates="data_addons")

    __table_args__ = (
        CheckConstraint('data_amount_gb > 0', name='chk_addon_data_amount_positive'),
        CheckConstraint('addon_price >= 0', name='chk_addon_price_positive'),
    )