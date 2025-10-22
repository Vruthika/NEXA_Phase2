from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Enum, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TransactionType(enum.Enum):
    PREPAID_RECHARGE = "prepaid_recharge"
    POSTPAID_BILL_PAYMENT = "postpaid_bill_payment"
    TOPUP_PURCHASE = "topup_purchase"

class PaymentMethod(enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    UPI = "upi"

class PaymentStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"

class DiscountType(enum.Enum):
    OFFER = "offer"
    REFERRAL = "referral"

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.plan_id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.offer_id"))
    recipient_phone_number = Column(String(20), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    original_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    discount_type = Column(Enum(DiscountType))
    final_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    transaction_date = Column(DateTime, default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    plan = relationship("Plan", back_populates="transactions")
    offer = relationship("Offer", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transaction", uselist=False)
    active_topup = relationship("ActiveTopup", back_populates="transaction", uselist=False)

    __table_args__ = (
        CheckConstraint('original_amount >= 0', name='chk_transaction_original_amount_positive'),
        CheckConstraint('discount_amount >= 0', name='chk_transaction_discount_amount_positive'),
        CheckConstraint('final_amount >= 0', name='chk_transaction_final_amount_positive'),
    )