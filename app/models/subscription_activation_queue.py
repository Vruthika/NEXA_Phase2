from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class SubscriptionActivationQueue(Base):
    __tablename__ = "subscription_activation_queue"
    
    queue_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.subscription_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    expected_activation_date = Column(DateTime, nullable=False)
    expected_expiry_date = Column(DateTime, nullable=False)
    queue_position = Column(Integer, nullable=False)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="subscription_queues")
    customer = relationship("Customer", back_populates="subscription_queues")

    __table_args__ = (
        CheckConstraint('queue_position > 0', name='chk_queue_position_positive'),
    )