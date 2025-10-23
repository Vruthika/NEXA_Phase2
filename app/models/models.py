from sqlalchemy import (
    Column, String, Integer, BigInteger, DateTime, Boolean, Enum, Text,
    DECIMAL, JSON, ForeignKey, Date, CheckConstraint, func
)
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime  


Base = declarative_base()

# ENUM DEFINITIONS

class AccountStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class PlanType(str, enum.Enum):
    prepaid = "prepaid"
    postpaid = "postpaid"

class PlanStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class TransactionType(str, enum.Enum):
    prepaid_recharge = "prepaid_recharge"
    postpaid_bill_payment = "postpaid_bill_payment"
    topup_purchase = "topup_purchase"

class DiscountType(str, enum.Enum):
    offer = "offer"
    referral = "referral"

class PaymentMethod(str, enum.Enum):
    credit_card = "credit_card"
    debit_card = "debit_card"
    net_banking = "net_banking"
    upi = "upi"

class PaymentStatus(str, enum.Enum):
    success = "success"
    failed = "failed"

class TopupStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    exhausted = "exhausted"
    expired = "expired"

class PostpaidStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    cancelled = "cancelled"

class ReferralStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    expired = "expired"

class AddonStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    fully_used = "fully_used"

class NotificationType(str, enum.Enum):
    low_balance = "low_balance"
    plan_expiry = "plan_expiry"
    promotional = "promotional"
    payment_success = "payment_success"
    payment_failure = "payment_failure"
    postpaid_due_date = "postpaid_due_date"
    referral_bonus = "referral_bonus"
    inactivity_warning = "inactivity_warning"
    plan_queued = "plan_queued"
    plan_activated = "plan_activated"
    data_exhausted = "data_exhausted"
    addon_offered = "addon_offered"
    topup_activated = "topup_activated"
    topup_exhausted = "topup_exhausted"
    daily_limit_reached = "daily_limit_reached"

class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"

# TABLE MODELS

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(Enum(AccountStatus), default=AccountStatus.active)
    full_name = Column(String(255), nullable=False)
    profile_picture_url = Column(String(300))
    last_active_plan_date = Column(DateTime)
    days_inactive = Column(Integer, default=0)
    inactivity_status_updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())  # Change back
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Change back
    
    # Relationships
    transactions = relationship("Transaction", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    subscription_queue = relationship("SubscriptionActivationQueue", back_populates="customer")
    active_topups = relationship("ActiveTopup", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")
    postpaid_activations = relationship("PostpaidActivation", back_populates="customer")
    
    # Linked accounts relationships
    linked_accounts_primary = relationship(
        "LinkedAccount", 
        foreign_keys="[LinkedAccount.primary_customer_id]", 
        back_populates="primary_customer"
    )
    linked_accounts_secondary = relationship(
        "LinkedAccount", 
        foreign_keys="[LinkedAccount.linked_customer_id]", 
        back_populates="linked_customer"
    )
    
    # Referral program relationships
    referrer_programs = relationship(
        "ReferralProgram", 
        foreign_keys="[ReferralProgram.referrer_customer_id]", 
        back_populates="referrer_customer"
    )
    referee_programs = relationship(
        "ReferralProgram", 
        foreign_keys="[ReferralProgram.referee_customer_id]", 
        back_populates="referee_customer"
    )
    referral_discounts = relationship("ReferralDiscount", back_populates="customer")
    referral_usage_logs = relationship("ReferralUsageLog", back_populates="used_by_customer")
    
    # Postpaid secondary numbers relationship
    postpaid_secondary_numbers = relationship("PostpaidSecondaryNumber", back_populates="customer")


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())  # Change back
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Change back
    
    # Relationships
    backups = relationship("Backup", back_populates="admin")
    restores = relationship("Restore", back_populates="admin")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    plans = relationship("Plan", back_populates="category")


class Plan(Base):
    __tablename__ = "plans"

    plan_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey("categories.category_id"), nullable=False)
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(Enum(PlanType), nullable=False)
    is_topup = Column(Boolean, default=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    validity_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    data_allowance_gb = Column(DECIMAL(5, 2))
    daily_data_limit_gb = Column(DECIMAL(5, 2))
    talktime_allowance_minutes = Column(Integer)
    sms_allowance = Column(Integer)
    benefits = Column(JSON)
    is_featured = Column(Boolean, default=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.active)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="plans")
    offers = relationship("Offer", back_populates="plan")
    transactions = relationship("Transaction", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")
    postpaid_activations = relationship("PostpaidActivation", back_populates="plan")
    active_topups = relationship("ActiveTopup", back_populates="plan")


class Offer(Base):
    __tablename__ = "offers"

    offer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_id = Column(BigInteger, ForeignKey("plans.plan_id"), nullable=False)
    discounted_price = Column(DECIMAL(10, 2), nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    plan = relationship("Plan", back_populates="offers")
    transactions = relationship("Transaction", back_populates="offer")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("plans.plan_id"), nullable=False)
    offer_id = Column(BigInteger, ForeignKey("offers.offer_id"))
    recipient_phone_number = Column(String(20), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    original_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    discount_type = Column(Enum(DiscountType))
    final_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    transaction_date = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    plan = relationship("Plan", back_populates="transactions")
    offer = relationship("Offer", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transaction", uselist=False)
    active_topup = relationship("ActiveTopup", back_populates="transaction", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("plans.plan_id"), nullable=False)
    transaction_id = Column(BigInteger, ForeignKey("transactions.transaction_id"), nullable=False)
    is_topup = Column(Boolean, default=False)
    activation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    data_balance_gb = Column(DECIMAL(5, 2))
    daily_data_limit_gb = Column(DECIMAL(5, 2))
    daily_data_used_gb = Column(DECIMAL(5, 2), default=0.00)
    last_daily_reset = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    transaction = relationship("Transaction", back_populates="subscription")
    activation_queue = relationship("SubscriptionActivationQueue", back_populates="subscription", uselist=False)
    active_topups = relationship("ActiveTopup", back_populates="base_subscription")


class SubscriptionActivationQueue(Base):
    __tablename__ = "subscription_activation_queue"

    queue_id = Column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id = Column(BigInteger, ForeignKey("subscriptions.subscription_id"), unique=True, nullable=False)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    expected_activation_date = Column(DateTime, nullable=False)
    expected_expiry_date = Column(DateTime, nullable=False)
    queue_position = Column(Integer, nullable=False)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="activation_queue")
    customer = relationship("Customer", back_populates="subscription_queue")


class ActiveTopup(Base):
    __tablename__ = "active_topups"

    topup_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    base_subscription_id = Column(BigInteger, ForeignKey("subscriptions.subscription_id", ondelete="CASCADE"), nullable=False)
    topup_plan_id = Column(BigInteger, ForeignKey("plans.plan_id"), nullable=False)
    transaction_id = Column(BigInteger, ForeignKey("transactions.transaction_id"), nullable=False)
    topup_data_gb = Column(DECIMAL(5, 2), nullable=False)
    data_remaining_gb = Column(DECIMAL(5, 2), nullable=False)
    activation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(Enum(TopupStatus), default=TopupStatus.pending)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="active_topups")
    base_subscription = relationship("Subscription", back_populates="active_topups")
    plan = relationship("Plan", back_populates="active_topups")
    transaction = relationship("Transaction", back_populates="active_topup")


class LinkedAccount(Base):
    __tablename__ = "linked_accounts"

    linked_account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    primary_customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    linked_phone_number = Column(String(20), nullable=False)
    linked_customer_id = Column(BigInteger, ForeignKey("customers.customer_id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    primary_customer = relationship(
        "Customer", 
        foreign_keys=[primary_customer_id], 
        back_populates="linked_accounts_primary"
    )
    linked_customer = relationship(
        "Customer", 
        foreign_keys=[linked_customer_id], 
        back_populates="linked_accounts_secondary"
    )


class PostpaidActivation(Base):
    __tablename__ = "postpaid_activations"

    activation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    plan_id = Column(BigInteger, ForeignKey("plans.plan_id"), nullable=False)
    primary_number = Column(String(20), nullable=False)
    billing_cycle_start = Column(DateTime, nullable=False)
    billing_cycle_end = Column(DateTime, nullable=False)
    base_data_allowance_gb = Column(DECIMAL(5, 2), nullable=False)
    current_data_balance_gb = Column(DECIMAL(5, 2), nullable=False)
    data_used_gb = Column(DECIMAL(5, 2), default=0.00)
    base_amount = Column(DECIMAL(10, 2), nullable=False)
    total_amount_due = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(PostpaidStatus), default=PostpaidStatus.active)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="postpaid_activations")
    plan = relationship("Plan", back_populates="postpaid_activations")
    secondary_numbers = relationship("PostpaidSecondaryNumber", back_populates="postpaid_activation", cascade="all, delete-orphan")
    data_addons = relationship("PostpaidDataAddon", back_populates="postpaid_activation")


class PostpaidSecondaryNumber(Base):
    __tablename__ = "postpaid_secondary_numbers"

    secondary_id = Column(BigInteger, primary_key=True, autoincrement=True)
    activation_id = Column(BigInteger, ForeignKey("postpaid_activations.activation_id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"))
    added_date = Column(DateTime, server_default=func.now())
    
    # Relationships
    postpaid_activation = relationship("PostpaidActivation", back_populates="secondary_numbers")
    customer = relationship("Customer", back_populates="postpaid_secondary_numbers")


class PostpaidDataAddon(Base):
    __tablename__ = "postpaid_data_addons"

    addon_id = Column(BigInteger, primary_key=True, autoincrement=True)
    activation_id = Column(BigInteger, ForeignKey("postpaid_activations.activation_id"), nullable=False)
    addon_name = Column(String(100), nullable=False)
    data_amount_gb = Column(DECIMAL(5, 2), nullable=False)
    addon_price = Column(DECIMAL(10, 2), nullable=False)
    purchased_date = Column(DateTime, server_default=func.now())
    valid_until = Column(DateTime, nullable=False)
    status = Column(Enum(AddonStatus), default=AddonStatus.active)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    postpaid_activation = relationship("PostpaidActivation", back_populates="data_addons")


class ReferralProgram(Base):
    __tablename__ = "referral_program"

    referral_id = Column(BigInteger, primary_key=True, autoincrement=True)
    referrer_customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    referee_phone_number = Column(String(20), nullable=False)
    referral_code = Column(String(20), unique=True, nullable=False)
    status = Column(Enum(ReferralStatus), default=ReferralStatus.pending)
    referee_customer_id = Column(BigInteger, ForeignKey("customers.customer_id"))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    referrer_customer = relationship(
        "Customer", 
        foreign_keys=[referrer_customer_id], 
        back_populates="referrer_programs"
    )
    referee_customer = relationship(
        "Customer", 
        foreign_keys=[referee_customer_id], 
        back_populates="referee_programs"
    )
    referral_discounts = relationship("ReferralDiscount", back_populates="referral_program")
    usage_logs = relationship("ReferralUsageLog", back_populates="referral_program")


class ReferralDiscount(Base):
    __tablename__ = "referral_discounts"

    discount_id = Column(BigInteger, primary_key=True, autoincrement=True)
    referral_id = Column(BigInteger, ForeignKey("referral_program.referral_id"), nullable=False)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=10.00)
    is_used = Column(Boolean, default=False)
    valid_until = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    used_at = Column(DateTime)
    
    # Relationships
    referral_program = relationship("ReferralProgram", back_populates="referral_discounts")
    customer = relationship("Customer", back_populates="referral_discounts")


class ReferralUsageLog(Base):
    __tablename__ = "referral_usage_log"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    referral_id = Column(BigInteger, ForeignKey("referral_program.referral_id"), nullable=False)
    used_by_phone = Column(String(20), nullable=False)
    used_by_customer_id = Column(BigInteger, ForeignKey("customers.customer_id"))
    used_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    referral_program = relationship("ReferralProgram", back_populates="usage_logs")
    used_by_customer = relationship("Customer", back_populates="referral_usage_logs")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.customer_id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="notifications")


class Backup(Base):
    __tablename__ = "backup"

    backup_id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey("admins.admin_id"), nullable=False)  # Fixed to "admins"
    file_name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    type = Column(String(20), CheckConstraint("type IN ('auto', 'manual')"))
    date = Column(Date, server_default=func.current_date())
    data_list = Column(JSON, nullable=False)
    
    # Relationships
    admin = relationship("Admin", back_populates="backups")


class Restore(Base):
    __tablename__ = "restore"

    restore_id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey("admins.admin_id"), nullable=False)  # Fixed to "admins"
    file_name = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    type = Column(String(20), CheckConstraint("type IN ('auto', 'manual')"))
    date = Column(Date, server_default=func.current_date())
    data_list = Column(JSON, nullable=False)
    
    # Relationships
    admin = relationship("Admin", back_populates="restores")