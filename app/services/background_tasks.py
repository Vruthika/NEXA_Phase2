# app/services/background_tasks.py
import asyncio
from app.database import SessionLocal
from app.services.subscription_service import subscription_service

async def process_expired_subscriptions_periodically():
    """Background task to process expired subscriptions every hour"""
    while True:
        try:
            db = SessionLocal()
            subscription_service.process_expired_subscriptions(db)
            db.close()
            print("✅ Processed expired subscriptions")
        except Exception as e:
            print(f"❌ Error processing expired subscriptions: {e}")
        
        # Wait for 1 hour before next run
        await asyncio.sleep(3600)