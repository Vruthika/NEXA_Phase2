import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.subscription_service import subscription_service
from app.services.automated_notifications import automated_notifications
from app.models.models import Subscription, ActiveTopup, PostpaidActivation
from app.crud.crud_token import crud_token

async def process_expired_subscriptions_periodically():
    """Background task to process expired subscriptions every hour"""
    while True:
        try:
            db = SessionLocal()
            
            # Process expired subscriptions first
            subscription_service.process_expired_subscriptions(db)
            
            # Check for upcoming expiries and send notifications
            await check_upcoming_expiries(db)
            
            # Check for low data balance (200MB threshold)
            await check_low_data_balance(db)
            
            # Check for postpaid bill due dates
            await check_postpaid_due_dates(db)
            
            db.close()
            print("✅ Processed automated notifications")
            
        except Exception as e:
            print(f"❌ Error processing automated notifications: {e}")
        
        # Wait for 1 hour before next run
        await asyncio.sleep(3600)
        
async def check_upcoming_expiries(db: Session):
    """Check for subscriptions/topups expiring soon and send notifications"""
    current_time = datetime.utcnow()
    
    # Check subscriptions expiring in next 24 hours
    expiry_threshold = current_time + timedelta(hours=24)
    
    upcoming_expiries = db.query(Subscription).filter(
        Subscription.expiry_date <= expiry_threshold,
        Subscription.expiry_date > current_time,
        Subscription.activation_date.isnot(None) 
    ).all()
    
    for subscription in upcoming_expiries:
        hours_until_expiry = (subscription.expiry_date - current_time).total_seconds() / 3600
        
        # Only notify if expiring within 24 hours and not notified recently
        if hours_until_expiry <= 24:
            automated_notifications.trigger_plan_expiry_notification(
                db, 
                subscription.customer_id, 
                subscription.plan.plan_name, 
                subscription.expiry_date
            )
            print(f"📅 Sent expiry notification for subscription {subscription.subscription_id}")
    
    # Check topups expiring soon
    upcoming_topups = db.query(ActiveTopup).filter(
        ActiveTopup.expiry_date <= expiry_threshold,
        ActiveTopup.expiry_date > current_time,
        ActiveTopup.status == 'active'
    ).all()
    
    for topup in upcoming_topups:
        hours_until_expiry = (topup.expiry_date - current_time).total_seconds() / 3600
        
        if hours_until_expiry <= 24:
            automated_notifications.trigger_plan_expiry_notification(
                db,
                topup.customer_id,
                f"Topup {topup.topup_data_gb}GB",
                topup.expiry_date
            )
            print(f"📅 Sent expiry notification for topup {topup.topup_id}")

async def check_low_data_balance(db: Session):
    """Check for low data balance and send notifications - 200MB threshold"""
    current_time = datetime.utcnow()
    
    # Check subscriptions with low data balance (< 200MB = 0.2GB)
    low_balance_subs = db.query(Subscription).filter(
        Subscription.data_balance_gb.isnot(None),
        Subscription.data_balance_gb < 0.2,  
        Subscription.expiry_date > current_time
    ).all()
    
    for subscription in low_balance_subs:
        # Convert GB to MB for the notification message
        balance_mb = float(subscription.data_balance_gb) * 1024
        automated_notifications.trigger_low_balance_notification(
            db,
            subscription.customer_id,
            balance_mb 
        )
        print(f"⚠️ Sent low balance notification for subscription {subscription.subscription_id}: {balance_mb:.0f}MB")
    
    # Check postpaid activations with low data (< 200MB)
    low_balance_postpaid = db.query(PostpaidActivation).filter(
        PostpaidActivation.current_data_balance_gb < 0.2,
        PostpaidActivation.status == 'active'
    ).all()
    
    for activation in low_balance_postpaid:
        # Convert GB to MB for the notification message
        balance_mb = float(activation.current_data_balance_gb) * 1024
        automated_notifications.trigger_low_balance_notification(
            db,
            activation.customer_id,
            balance_mb   
        )
        print(f"⚠️ Sent low balance notification for postpaid activation {activation.activation_id}: {balance_mb:.0f}MB")
        
async def check_postpaid_due_dates(db: Session):
    """Check for postpaid bills due soon"""
    current_time = datetime.utcnow()
    due_threshold = current_time + timedelta(days=3)  # 3 days before due
    
    due_activations = db.query(PostpaidActivation).filter(
        PostpaidActivation.billing_cycle_end <= due_threshold,
        PostpaidActivation.billing_cycle_end > current_time,
        PostpaidActivation.status == 'active'
    ).all()
    
    for activation in due_activations:
        days_until_due = (activation.billing_cycle_end - current_time).days
        
        # Use the automated notifications method
        automated_notifications.trigger_automated_notification(
            db,
            activation.customer_id,
            "postpaid_due_date",
            "📅 Postpaid Bill Due Soon",
            f"Your postpaid bill of ₹{activation.total_amount_due} is due in {days_until_due} days. Please pay before {activation.billing_cycle_end.strftime('%d %b %Y')}.",
            "push"
        )
        print(f"💳 Sent due date notification for postpaid activation {activation.activation_id}")
        

def cleanup_expired_tokens(db: Session):
    """Clean up expired blacklisted tokens"""
    try:
        deleted_count = crud_token.cleanup_expired_tokens(db)
        print(f"Cleaned up {deleted_count} expired blacklisted tokens")
    except Exception as e:
        print(f"Error cleaning up expired tokens: {e}")