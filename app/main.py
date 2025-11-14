from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routes import admin, auth, customer_operations
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

# Customer-facing routes
app.include_router(auth.router)
app.include_router(customer_operations.router)

# Admin-only routes
app.include_router(admin.admin_router, prefix="/admin")
app.include_router(admin.category_router, prefix="/admin")
app.include_router(admin.plan_router, prefix="/admin")
app.include_router(admin.offer_router, prefix="/admin")
app.include_router(admin.transaction_router, prefix="/admin")
app.include_router(admin.subscription_router, prefix="/admin")
app.include_router(admin.customer_router, prefix="/admin")
app.include_router(admin.dashboard_router, prefix="/admin")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )