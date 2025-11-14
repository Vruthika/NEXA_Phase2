# create_fixed_test_data.py
from app.database import SessionLocal
from app.models.models import Customer, Plan, Subscription, SubscriptionActivationQueue, Transaction
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

def create_fixed_test_data():
    db = SessionLocal()
    try:
        print("🔄 Creating fixed test data...")
        
        # Create or get test customer
        customer = db.query(Customer).filter(Customer.phone_number == "9345899429").first()
        if not customer:
            customer = Customer(
                phone_number="9345899429",
                password_hash=get_password_hash("vruthika"),
                full_name="Vruthika Test",
                account_status="active"
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"✅ Created customer: {customer.full_name}")
        else:
            print(f"✅ Using existing customer: {customer.full_name}")
        
        # Get some active plans
        plans = db.query(Plan).filter(Plan.status == "active").all()
        if not plans:
            print("❌ No active plans found. Please create plans first.")
            return
        
        print(f"✅ Found {len(plans)} active plans")
        
        current_time = datetime.utcnow()
        
        # Clear existing test data for this customer
        db.query(Subscription).filter(Subscription.customer_id == customer.customer_id).delete()
        db.query(SubscriptionActivationQueue).filter(SubscriptionActivationQueue.customer_id == customer.customer_id).delete()
        db.query(Transaction).filter(Transaction.customer_id == customer.customer_id).delete()
        
        # Create active subscription with transaction
        active_plan = random.choice(plans)
        
        # Create transaction for active subscription
        active_transaction = Transaction(
            customer_id=customer.customer_id,
            plan_id=active_plan.plan_id,
            recipient_phone_number=customer.phone_number,
            transaction_type="prepaid_recharge",
            original_amount=float(active_plan.price),
            discount_amount=0.0,
            final_amount=float(active_plan.price),
            payment_method="upi",
            payment_status="success",
            transaction_date=current_time - timedelta(days=2)
        )
        db.add(active_transaction)
        db.commit()
        db.refresh(active_transaction)
        
        # Create active subscription
        active_sub = Subscription(
            customer_id=customer.customer_id,
            phone_number=customer.phone_number,
            plan_id=active_plan.plan_id,
            transaction_id=active_transaction.transaction_id,
            is_topup=active_plan.is_topup,
            activation_date=current_time - timedelta(days=2),
            expiry_date=current_time + timedelta(days=28),
            data_balance_gb=float(active_plan.data_allowance_gb) if active_plan.data_allowance_gb else None,
            daily_data_limit_gb=float(active_plan.daily_data_limit_gb) if active_plan.daily_data_limit_gb else None,
            daily_data_used_gb=1.5,
            last_daily_reset=current_time
        )
        db.add(active_sub)
        db.commit()
        db.refresh(active_sub)
        print(f"✅ Created active subscription: {active_plan.plan_name}")
        
        # Create queued subscription with transaction
        queued_plan = random.choice([p for p in plans if p.plan_id != active_plan.plan_id])
        
        # Create transaction for queued subscription
        queued_transaction = Transaction(
            customer_id=customer.customer_id,
            plan_id=queued_plan.plan_id,
            recipient_phone_number=customer.phone_number,
            transaction_type="prepaid_recharge",
            original_amount=float(queued_plan.price),
            discount_amount=0.0,
            final_amount=float(queued_plan.price),
            payment_method="upi",
            payment_status="success",
            transaction_date=current_time
        )
        db.add(queued_transaction)
        db.commit()
        db.refresh(queued_transaction)
        
        # Create queued subscription
        queued_sub = Subscription(
            customer_id=customer.customer_id,
            phone_number=customer.phone_number,
            plan_id=queued_plan.plan_id,
            transaction_id=queued_transaction.transaction_id,
            is_topup=queued_plan.is_topup,
            activation_date=None,
            expiry_date=current_time + timedelta(days=queued_plan.validity_days),
            data_balance_gb=float(queued_plan.data_allowance_gb) if queued_plan.data_allowance_gb else None,
            daily_data_limit_gb=float(queued_plan.daily_data_limit_gb) if queued_plan.daily_data_limit_gb else None,
            daily_data_used_gb=0.0,
            last_daily_reset=None
        )
        db.add(queued_sub)
        db.commit()
        db.refresh(queued_sub)
        
        # Add to activation queue
        queue_item = SubscriptionActivationQueue(
            subscription_id=queued_sub.subscription_id,
            customer_id=customer.customer_id,
            phone_number=customer.phone_number,
            expected_activation_date=current_time + timedelta(days=28),
            expected_expiry_date=current_time + timedelta(days=28 + queued_plan.validity_days),
            queue_position=1
        )
        db.add(queue_item)
        db.commit()
        print(f"✅ Created queued subscription: {queued_plan.plan_name} (position 1)")
        
        # Update customer's last_active_plan_date
        customer.last_active_plan_date = active_sub.activation_date
        customer.days_inactive = 0
        customer.inactivity_status_updated_at = current_time
        db.commit()
        
        print("\n🎉 Fixed test data created successfully!")
        print(f"   Customer: {customer.full_name} (ID: {customer.customer_id})")
        print(f"   Last Active Plan Date: {customer.last_active_plan_date}")
        
        # Verify data was created
        active_subs = db.query(Subscription).filter(
            Subscription.customer_id == customer.customer_id,
            Subscription.expiry_date > current_time
        ).count()
        
        queued_subs = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer.customer_id,
            SubscriptionActivationQueue.processed_at.is_(None)
        ).count()
        
        transactions_count = db.query(Transaction).filter(
            Transaction.customer_id == customer.customer_id
        ).count()
        
        print(f"   Verification - Active: {active_subs}, Queued: {queued_subs}, Transactions: {transactions_count}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_fixed_test_data()