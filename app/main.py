from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routes import admin, auth, customer_operations
import asyncio
from app.services.background_tasks import process_expired_subscriptions_periodically

# Import models to ensure they are registered with SQLAlchemy
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

# Customer-facing routes (no admin authentication)
app.include_router(auth.router)
app.include_router(customer_operations.router)

# Admin-only routes (require admin authentication)
app.include_router(admin.admin_router)
app.include_router(admin.category_router)
app.include_router(admin.plan_router)
app.include_router(admin.offer_router)
app.include_router(admin.transaction_router)
app.include_router(admin.subscription_router)
app.include_router(admin.customer_router)
app.include_router(admin.dashboard_router)

@app.on_event("startup")
async def startup_event():
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print(f"✅ Database tables created for {settings.APP_NAME}")
        
        # Create default admin if not exists
        from app.database import SessionLocal
        from app.crud.crud_admin import crud_admin
        
        db = SessionLocal()
        try:
            admin_user = crud_admin.get_by_email(db, settings.ADMIN_DEFAULT_EMAIL)
            if not admin_user:
                from app.schemas.admin import AdminCreate
                default_admin = AdminCreate(
                    name=settings.ADMIN_DEFAULT_NAME,
                    phone_number=settings.ADMIN_DEFAULT_PHONE,
                    email=settings.ADMIN_DEFAULT_EMAIL,
                    password=settings.ADMIN_DEFAULT_PASSWORD
                )
                created_admin = crud_admin.create(db, default_admin)
                print(f"✅ Default admin created: {created_admin.email}")
            else:
                print(f"✅ Default admin already exists: {admin_user.email}")
        except Exception as e:
            print(f"❌ Error with admin: {e}")
        finally:
            db.close()
        
        # Start background tasks
        asyncio.create_task(process_expired_subscriptions_periodically())
        print("✅ Background tasks started")
            
    except Exception as e:
        print(f"❌ Startup error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )