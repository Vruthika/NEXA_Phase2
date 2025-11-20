from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.models import Customer, Plan, Offer, ReferralDiscount, ReferralProgram, ReferralStatus, Transaction, Subscription, SubscriptionActivationQueue, Category
from app.core.auth import get_current_customer
from app.schemas.customer_operations import *
from app.crud import crud_customer, crud_subscription
from app.core.security import verify_password, get_password_hash
from app.crud.crud_customer import crud_customer
from app.services.automated_notifications import automated_notifications



# ==========================================================
# 👤 CUSTOMER PROFILE MANAGEMENT
# ==========================================================
profile_router = APIRouter(prefix="/customer", tags=["Customer Profile"])

@profile_router.get("/profile", response_model=CustomerProfileResponse)
async def get_customer_profile(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current customer's profile information.
    """
    # Directly update the last_active_plan_date based on current active subscriptions
    current_time = datetime.utcnow()
    
    # Find the most recent active subscription
    latest_active_subscription = db.query(Subscription).filter(
        Subscription.customer_id == current_customer.customer_id,
        Subscription.expiry_date > current_time
    ).order_by(Subscription.activation_date.desc()).first()
    
    if latest_active_subscription:
        # Update the customer's last_active_plan_date
        current_customer.last_active_plan_date = latest_active_subscription.activation_date
        current_customer.days_inactive = 0
        current_customer.inactivity_status_updated_at = current_time
        db.commit()
    
    # Refresh to get updated data
    db.refresh(current_customer)
    
    print(f"DEBUG: Customer {current_customer.customer_id} - last_active_plan_date: {current_customer.last_active_plan_date}")
    
    return current_customer

@profile_router.put("/profile", response_model=CustomerProfileResponse)
async def update_customer_profile(
    profile_update: CustomerProfileUpdate,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Update customer profile information.
    """
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_customer, field, value)
    
    current_customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_customer)
    
    return current_customer

@profile_router.post("/change-password")
async def change_customer_password(
    current_password: str = Query(..., description="Current password"),
    new_password: str = Query(..., description="New password"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Change customer password.
    """
    if not verify_password(current_password, current_customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
    
    current_customer.password_hash = get_password_hash(new_password)
    current_customer.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


# ==========================================================
# 📋 PLANS & OFFERS VIEWING
# ==========================================================
plans_offers_router = APIRouter(prefix="/customer", tags=["View Plans & Offers"])

@plans_offers_router.get("/plans", response_model=List[PlanResponseForCustomer])
async def get_plans_for_customer(
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all available plans for customers.
    """
    query = db.query(Plan).join(Category).filter(
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    )
    
    if plan_type:
        query = query.filter(Plan.plan_type == plan_type)
    
    if category_id:
        query = query.filter(Plan.category_id == category_id)
    
    plans = query.all()
    current_time = datetime.utcnow()
    
    response_plans = []
    for plan in plans:
        # Check for active offers for this plan
        active_offer = db.query(Offer).filter(
            Offer.plan_id == plan.plan_id,
            Offer.valid_from <= current_time,
            Offer.valid_until >= current_time
        ).first()
        
        has_active_offer = active_offer is not None
        offer_id = active_offer.offer_id if active_offer else None
        offer_price = float(active_offer.discounted_price) if active_offer else None
        
        # Calculate discount percentage if offer exists
        discount_percentage = None
        if active_offer:
            discount_percentage = round(
                ((float(plan.price) - float(active_offer.discounted_price)) / float(plan.price)) * 100, 
                2
            )
        
        response_plans.append(PlanResponseForCustomer(
            plan_id=plan.plan_id,
            category_name=plan.category.category_name,
            plan_name=plan.plan_name,
            plan_type=plan.plan_type,
            is_topup=plan.is_topup,
            price=float(plan.price),
            validity_days=plan.validity_days,
            description=plan.description,
            data_allowance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            talktime_allowance_minutes=plan.talktime_allowance_minutes,
            sms_allowance=plan.sms_allowance,
            benefits=plan.benefits,
            is_featured=plan.is_featured,
            has_active_offer=has_active_offer,
            offer_id=offer_id,
            offer_price=offer_price,
            discount_percentage=discount_percentage,
            offer_valid_until=active_offer.valid_until.strftime('%d.%m.%Y %H:%M') if active_offer else None
        ))
    
    return response_plans

@plans_offers_router.get("/plans/{plan_id}", response_model=PlanResponseForCustomer)
async def get_plan_details(
    plan_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific plan.
    """
    plan = db.query(Plan).join(Category).filter(
        Plan.plan_id == plan_id,
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    current_time = datetime.utcnow()
    
    # Check for active offers for this plan - FIXED QUERY
    active_offer = db.query(Offer).filter(
        Offer.plan_id == plan.plan_id,
        Offer.valid_from <= current_time,
        Offer.valid_until >= current_time
    ).first()
    
    has_active_offer = active_offer is not None
    offer_id = active_offer.offer_id if active_offer else None
    offer_price = float(active_offer.discounted_price) if active_offer else None
    
    # Calculate discount percentage if offer exists
    discount_percentage = None
    if active_offer:
        discount_percentage = round(
            ((float(plan.price) - float(active_offer.discounted_price)) / float(plan.price)) * 100, 
            2
        )
    
    return PlanResponseForCustomer(
        plan_id=plan.plan_id,
        category_name=plan.category.category_name,
        plan_name=plan.plan_name,
        plan_type=plan.plan_type,
        is_topup=plan.is_topup,
        price=float(plan.price),
        validity_days=plan.validity_days,
        description=plan.description,
        data_allowance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
        daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
        talktime_allowance_minutes=plan.talktime_allowance_minutes,
        sms_allowance=plan.sms_allowance,
        benefits=plan.benefits,
        is_featured=plan.is_featured,
        has_active_offer=has_active_offer,
        offer_id=offer_id,
        offer_price=offer_price,
        discount_percentage=discount_percentage,
        offer_valid_until=active_offer.valid_until.strftime('%d.%m.%Y %H:%M') if active_offer else None
    )
    
@plans_offers_router.get("/offers", response_model=List[OfferResponseForCustomer])
async def get_offers_for_customer(
    plan_id: Optional[int] = Query(None, description="Filter by plan"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all active offers for customers.
    """
    current_time = datetime.utcnow()
    
    query = db.query(Offer).join(Plan).filter(
        Offer.valid_from <= current_time,
        Offer.valid_until >= current_time,
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    )
    
    if plan_id:
        query = query.filter(Offer.plan_id == plan_id)
    
    offers = query.all()
    
    response_offers = []
    for offer in offers:
        discount_percentage = ((float(offer.plan.price) - float(offer.discounted_price)) / float(offer.plan.price)) * 100
        
        response_offers.append(OfferResponseForCustomer(
            offer_id=offer.offer_id,
            plan_name=offer.plan.plan_name,
            offer_name=offer.offer_name,
            description=offer.description,
            original_price=float(offer.plan.price),
            discounted_price=float(offer.discounted_price),
            discount_percentage=round(discount_percentage, 2),
            valid_from=offer.valid_from.strftime('%d.%m.%Y %H:%M'),
            valid_until=offer.valid_until.strftime('%d.%m.%Y %H:%M')
        ))
    
    return response_offers

@plans_offers_router.get("/categories")
async def get_categories(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all plan categories.
    """
    categories = db.query(Category).all()
    return [{"category_id": cat.category_id, "category_name": cat.category_name} for cat in categories]


# ==========================================================
# 🔄 RECHARGE FUNCTIONALITY
# ==========================================================
recharge_router = APIRouter(prefix="/customer", tags=["Recharge"])

@recharge_router.post("/recharge", response_model=RechargeResponse)
async def create_recharge(
    recharge_data: RechargeRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Create a new recharge transaction and handle subscription logic.
    Applies referral discounts and completes referral process for first recharge.
    """
    from app.services.subscription_service import subscription_service
    from app.crud.crud_referral import crud_referral
    from app.services.automated_notifications import automated_notifications
    
    # Verify plan exists and is active
    plan = db.query(Plan).filter(
        Plan.plan_id == recharge_data.plan_id,
        Plan.status == "active",
        Plan.deleted_at.is_(None)
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or inactive"
        )
    
    # Check for available referral discounts for this customer
    referral_discounts = crud_referral.get_customer_referral_discounts(db, current_customer.customer_id)
    active_referral_discount = None
    
    if referral_discounts:
        # Use the first available referral discount
        active_referral_discount = referral_discounts[0]
    
    # Verify offer if provided
    offer = None
    if recharge_data.offer_id and recharge_data.offer_id > 0:
        offer = db.query(Offer).filter(
            Offer.offer_id == recharge_data.offer_id,
            Offer.plan_id == recharge_data.plan_id,
            Offer.valid_from <= datetime.utcnow(),
            Offer.valid_until >= datetime.utcnow()
        ).first()
        
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found or expired"
            )
    
    # Calculate amounts - PRIORITIZE REFERRAL DISCOUNT OVER OFFER
    original_amount = float(plan.price)
    discount_amount = 0.0
    discount_type = None
    referral_message = ""
    
    if active_referral_discount:
        # Apply referral discount
        discount_percentage = float(active_referral_discount.discount_percentage)
        discount_amount = (original_amount * discount_percentage) / 100
        final_amount = original_amount - discount_amount
        discount_type = "referral"
        
        # Mark the referral discount as used
        crud_referral.mark_discount_used(db, active_referral_discount.discount_id, current_customer.customer_id)
        
        referral_message = f" Applied {discount_percentage}% referral discount!"
        print(f"DEBUG: Applied referral discount {discount_percentage}% for customer {current_customer.customer_id}")
        
    elif offer:
        # Apply offer discount
        discounted_price = float(offer.discounted_price)
        discount_amount = original_amount - discounted_price
        final_amount = discounted_price
        discount_type = "offer"
        referral_message = ""
    else:
        # No discounts
        final_amount = original_amount
        discount_type = None
        referral_message = ""
    
    # Create transaction
    transaction = Transaction(
        customer_id=current_customer.customer_id,
        plan_id=recharge_data.plan_id,
        offer_id=recharge_data.offer_id if recharge_data.offer_id and recharge_data.offer_id > 0 else None,
        recipient_phone_number=recharge_data.recipient_phone_number,
        transaction_type="prepaid_recharge",
        original_amount=original_amount,
        discount_amount=discount_amount,
        discount_type=discount_type,
        final_amount=final_amount,
        payment_method=recharge_data.payment_method,
        payment_status="success"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Trigger recharge success notification
    automated_notifications.trigger_recharge_success_notification(
        db, current_customer.customer_id, plan.plan_name, final_amount
    )
    
    current_time = datetime.utcnow()
    
    # Check if this is the customer's first successful recharge
    previous_recharges = db.query(Transaction).filter(
        Transaction.customer_id == current_customer.customer_id,
        Transaction.payment_status == "success",
        Transaction.transaction_id != transaction.transaction_id  # Exclude current transaction
    ).count()

    # If this is the first recharge, complete any pending referrals for this customer
    if previous_recharges == 0:
        print(f"DEBUG: First recharge for customer {current_customer.customer_id}, checking for pending referrals...")
        
        # Complete the referral if this customer was referred by someone
        completed_referral, error = crud_referral.complete_referral(
            db, current_customer.customer_id, current_customer.phone_number
        )
        
        if completed_referral:
            print(f"DEBUG: Referral completed successfully for customer: {current_customer.phone_number}")
            referral_message += " Referral completed! You earned rewards for your referrer."
        else:
            print(f"DEBUG: No referral to complete or error: {error}")
    
    # Check if customer has active subscriptions for this phone number
    active_subscriptions = db.query(Subscription).filter(
        Subscription.customer_id == current_customer.customer_id,
        Subscription.phone_number == recharge_data.recipient_phone_number,
        Subscription.expiry_date > current_time
    ).order_by(Subscription.expiry_date.desc()).all()
    
    # Handle topup plans differently - they should always activate immediately
    if plan.is_topup:
        # For topup plans, activate immediately regardless of existing subscriptions
        activation_date = current_time
        expiry_date = current_time + timedelta(days=plan.validity_days)
        
        subscription = Subscription(
            customer_id=current_customer.customer_id,
            phone_number=recharge_data.recipient_phone_number,
            plan_id=recharge_data.plan_id,
            transaction_id=transaction.transaction_id,
            is_topup=plan.is_topup,
            activation_date=activation_date,
            expiry_date=expiry_date,
            data_balance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=current_time
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # >>> TOPUP/IMMEDIATE ACTIVATION <<<
        automated_notifications.trigger_plan_activated_notification(
            db, current_customer.customer_id, plan.plan_name
        )
        
        # Update customer's last_active_plan_date
        current_customer.last_active_plan_date = current_time
        current_customer.days_inactive = 0
        current_customer.inactivity_status_updated_at = current_time
        db.commit()
        
        message = "Topup recharge successful! Your data has been added to your account." + referral_message
        
    elif not active_subscriptions:
        # No active subscription - activate immediately for regular plans
        activation_date = current_time
        expiry_date = current_time + timedelta(days=plan.validity_days)
        
        subscription = Subscription(
            customer_id=current_customer.customer_id,
            phone_number=recharge_data.recipient_phone_number,
            plan_id=recharge_data.plan_id,
            transaction_id=transaction.transaction_id,
            is_topup=plan.is_topup,
            activation_date=activation_date,
            expiry_date=expiry_date,
            data_balance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=current_time
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # >>> IMMEDIATE ACTIVATION <<<
        automated_notifications.trigger_plan_activated_notification(
            db, current_customer.customer_id, plan.plan_name
        )
        
        # Update customer's last_active_plan_date
        current_customer.last_active_plan_date = current_time
        current_customer.days_inactive = 0
        current_customer.inactivity_status_updated_at = current_time
        db.commit()
        
        message = "Recharge successful! Your plan is now active." + referral_message
        
    else:
        # Active subscription exists for regular plans - add to queue
        # Filter only BASE plans (not topups) to determine activation date
        base_plans = [sub for sub in active_subscriptions if not sub.is_topup]
        
        if base_plans:
            # Use the latest base plan expiry for activation
            latest_active_base_plan = base_plans[0]  # Already ordered by expiry_date desc
            activation_date = latest_active_base_plan.expiry_date
        else:
            # If no base plans found (shouldn't happen in normal flow), activate immediately
            activation_date = current_time
            
        expiry_date = activation_date + timedelta(days=plan.validity_days)
        
        # Create subscription with calculated activation date
        subscription = Subscription(
            customer_id=current_customer.customer_id,
            phone_number=recharge_data.recipient_phone_number,
            plan_id=recharge_data.plan_id,
            transaction_id=transaction.transaction_id,
            is_topup=plan.is_topup,
            activation_date=activation_date,  # Set to when current base plan expires
            expiry_date=expiry_date,
            data_balance_gb=float(plan.data_allowance_gb) if plan.data_allowance_gb else None,
            daily_data_limit_gb=float(plan.daily_data_limit_gb) if plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=activation_date  # Will reset when activated
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Only add BASE plans to activation queue (not topups)
        if not plan.is_topup:
            # Get next queue position
            queue_position = subscription_service.get_next_queue_position(
                db, current_customer.customer_id, recharge_data.recipient_phone_number
            )
            
            # Add to activation queue
            queue_item = SubscriptionActivationQueue(
                subscription_id=subscription.subscription_id,
                customer_id=current_customer.customer_id,
                phone_number=recharge_data.recipient_phone_number,
                expected_activation_date=activation_date,  
                expected_expiry_date=expiry_date,
                queue_position=queue_position
            )
            
            db.add(queue_item)
            db.commit()
            
            # >>> QUEUED ACTIVATION <<<
            automated_notifications.trigger_plan_queued_notification(
                db, current_customer.customer_id, plan.plan_name, queue_position, activation_date
            )
            
            message = f"Recharge successful! Your plan is queued (position {queue_position}) and will activate when your current plan expires on {activation_date.strftime('%d %b %Y')}." + referral_message
        else:
            # This shouldn't happen as topups are handled above, but just in case
            message = "Recharge successful! Your topup has been processed." + referral_message
    
    # Refresh to get updated data
    db.refresh(current_customer)
    
    return RechargeResponse(
        transaction_id=transaction.transaction_id,
        plan_name=plan.plan_name,
        final_amount=final_amount,
        payment_status=transaction.payment_status,
        message=message
    )

# ==========================================================
# 💳 TRANSACTION HISTORY
# ==========================================================
transaction_router = APIRouter(prefix="/customer", tags=["View Transactions"])

@transaction_router.get("/transactions", response_model=List[CustomerTransactionResponse])
async def get_customer_transactions(
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get customer's transaction history.
    """
    transactions = crud_customer.get_customer_transactions(
        db, current_customer.customer_id, skip=skip, limit=limit
    )
    
    response_transactions = []
    for transaction in transactions:
        plan = db.query(Plan).filter(Plan.plan_id == transaction.plan_id).first()
        
        response_transactions.append(CustomerTransactionResponse(
            transaction_id=transaction.transaction_id,
            plan_name=plan.plan_name if plan else "Unknown",
            recipient_phone_number=transaction.recipient_phone_number,
            transaction_type=transaction.transaction_type,
            original_amount=float(transaction.original_amount),
            discount_amount=float(transaction.discount_amount),
            final_amount=float(transaction.final_amount),
            payment_method=transaction.payment_method,
            payment_status=transaction.payment_status,
            transaction_date=transaction.transaction_date
        ))
    
    return response_transactions

@transaction_router.get("/transactions/{transaction_id}", response_model=CustomerTransactionResponse)
async def get_customer_transaction(
    transaction_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific transaction.
    """
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.customer_id == current_customer.customer_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    plan = db.query(Plan).filter(Plan.plan_id == transaction.plan_id).first()
    
    return CustomerTransactionResponse(
        transaction_id=transaction.transaction_id,
        plan_name=plan.plan_name if plan else "Unknown",
        recipient_phone_number=transaction.recipient_phone_number,
        transaction_type=transaction.transaction_type,
        original_amount=float(transaction.original_amount),
        discount_amount=float(transaction.discount_amount),
        final_amount=float(transaction.final_amount),
        payment_method=transaction.payment_method,
        payment_status=transaction.payment_status,
        transaction_date=transaction.transaction_date
    )

# ==========================================================
# 📱 SUBSCRIPTION MANAGEMENT
# ==========================================================
subscriptions_router = APIRouter(prefix="/customer", tags=["View Subscriptions"])

@subscriptions_router.get("/subscriptions/active", response_model=List[CustomerSubscriptionResponse])
async def get_customer_active_subscriptions(current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    from app.services.subscription_service import subscription_service
    
    # Process expired subscriptions before returning data
    subscription_service.process_expired_subscriptions(db)
    
    current_time = datetime.utcnow()
    
    subscriptions = db.query(Subscription).join(
        Plan, Subscription.plan_id == Plan.plan_id
    ).filter(
        Subscription.customer_id == current_customer.customer_id,
        Subscription.activation_date.isnot(None),  # Must be activated
        Subscription.activation_date <= current_time,  # Activation date has passed
        Subscription.expiry_date > current_time  # Not expired yet
    ).order_by(Subscription.expiry_date.asc()).all()  # Order by expiry date
    
    response_subscriptions = []
    for subscription in subscriptions:
        response_subscriptions.append(CustomerSubscriptionResponse(
            subscription_id=subscription.subscription_id,
            plan_name=subscription.plan.plan_name,
            phone_number=subscription.phone_number,
            is_topup=subscription.is_topup,
            activation_date=subscription.activation_date,
            expiry_date=subscription.expiry_date,
            data_balance_gb=float(subscription.data_balance_gb) if subscription.data_balance_gb else None,
            daily_data_limit_gb=float(subscription.daily_data_limit_gb) if subscription.daily_data_limit_gb else None,
            daily_data_used_gb=float(subscription.daily_data_used_gb) if subscription.daily_data_used_gb else None,
            status="active"
        ))
    
    return response_subscriptions

@subscriptions_router.get("/subscriptions/queue", response_model=List[CustomerQueueResponse])
async def get_customer_queued_subscriptions(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get customer's queued subscriptions waiting for activation.
    """
    from app.services.subscription_service import subscription_service
    
    # Process expired subscriptions before returning data
    subscription_service.process_expired_subscriptions(db)
    
    # Only get unprocessed queue items
    queue_items = db.query(SubscriptionActivationQueue).join(
        Subscription, SubscriptionActivationQueue.subscription_id == Subscription.subscription_id
    ).join(
        Plan, Subscription.plan_id == Plan.plan_id
    ).filter(
        SubscriptionActivationQueue.customer_id == current_customer.customer_id,
        SubscriptionActivationQueue.processed_at.is_(None)  # Only unprocessed items
    ).order_by(SubscriptionActivationQueue.queue_position).all()
    
    response_queue = []
    for item in queue_items:
        response_queue.append(CustomerQueueResponse(
            queue_id=item.queue_id,
            plan_name=item.subscription.plan.plan_name,
            phone_number=item.phone_number,
            queue_position=item.queue_position,
            expected_activation_date=item.expected_activation_date,
            expected_expiry_date=item.expected_expiry_date
        ))
    
    return response_queue

