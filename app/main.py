from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.models.models import BlacklistedToken


# Import routes
from app.mongo import close_mongo_client, get_mongo_client, get_mongo_db
from app.routes import auth
from app.routes.admin import admin_router, category_router, plan_router, offer_router, transactions_router, subscription_router, customer_router
from app.routes.customer import profile_router, plans_offers_router, recharge_router, transaction_router, subscriptions_router
from app.routes.customer_postpaid import plans_addons_router, activations_router,bill_router,secondary_numbers_router
from app.routes.admin_postpaid import router as admin_postpaid_activations_router
from app.routes.admin_postpaid import router1 as admin_postpaid_billing_router
from app.routes.customer_linked_accounts import router as customer_linked_accounts_router
from app.routes.admin_linked_accounts import router as admin_linked_accounts_router
from app.routes.customer_referral import router as customer_referral_router
from app.routes.admin_referral import router as admin_referral_router
from app.routes.customer_notifications import router as customer_notifications_router
from app.routes.admin_notifications import router as admin_notifications_router
from app.routes.admin_analytics import router as analytics_router
from app.routes.admin_backup_restore import router as backup_restore_router
from app.routes.admin_cms import router as admin_cms_router
from app.routes.customer_cms import router as customer_cms_router

import asyncio
from app.services.background_tasks import process_expired_subscriptions_periodically
from app.models import models

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection events - FIXED VERSION
@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB connection and store in app state
    client = get_mongo_client()
    app.state.mongo_client = client
    app.state.mongo_db = get_mongo_db()
    
    # Test the connection
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection established successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    # Close MongoDB connection
    close_mongo_client()
    print("MongoDB connection closed")

app.include_router(auth.router)
# Customer-facing routes
app.include_router(profile_router)
app.include_router(plans_offers_router)
app.include_router(recharge_router)
app.include_router(transaction_router)
app.include_router(subscriptions_router)
app.include_router(plans_addons_router)
app.include_router(activations_router)
app.include_router(bill_router)
app.include_router(secondary_numbers_router)
app.include_router(customer_linked_accounts_router)
app.include_router(customer_referral_router)
app.include_router(customer_notifications_router)
app.include_router(customer_cms_router)

# Admin-only routes
app.include_router(admin_router, prefix="/admin")
app.include_router(category_router, prefix="/admin")
app.include_router(plan_router, prefix="/admin")
app.include_router(offer_router, prefix="/admin")
app.include_router(transactions_router, prefix="/admin")
app.include_router(subscription_router, prefix="/admin")
app.include_router(customer_router, prefix="/admin")
app.include_router(admin_postpaid_activations_router, prefix="/admin")  
app.include_router(admin_postpaid_billing_router, prefix="/admin")  
app.include_router(admin_linked_accounts_router, prefix="/admin")
app.include_router(admin_referral_router, prefix="/admin")
app.include_router(admin_notifications_router, prefix="/admin")
app.include_router(analytics_router, prefix="/admin")
app.include_router(backup_restore_router, prefix="/admin")
app.include_router(admin_cms_router, prefix="/admin")

   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )