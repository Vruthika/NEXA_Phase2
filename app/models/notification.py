from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class NotificationType(enum.Enum):
    LOW_BALANCE = "low_balance"
    PLAN_EXPIRY = "plan_expiry"
    PROMOTIONAL = "promotional"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILURE = "payment_failure"
    POSTPAID_DUE_DATE = "postpaid_due_date"
    REFERRAL_BONUS = "referral_bonus"
    INACTIVITY_WARNING = "inactivity_warning"
    PLAN_QUEUED = "plan_queued"
    PLAN_ACTIVATED = "plan_activated"
    DATA_EXHAUSTED = "data_exhausted"
    ADDON_OFFERED = "addon_offered"
    TOPUP_ACTIVATED = "topup_activated"
    TOPUP_EXHAUSTED = "topup_exhausted"
    DAILY_LIMIT_REACHED = "daily_limit_reached"

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="notifications")