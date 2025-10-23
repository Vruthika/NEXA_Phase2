from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routes import admin, auth

# Import ALL models explicitly to ensure they are registered
from app.models.models import (
    Admin, Customer, Category, Plan, Offer, Transaction, 
    Subscription, SubscriptionActivationQueue, ActiveTopup,
    LinkedAccount, PostpaidActivation, PostpaidSecondaryNumber,
    PostpaidDataAddon, ReferralProgram, ReferralDiscount,
    ReferralUsageLog, Notification, Backup, Restore
)

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

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to NEXA Mobile Recharge System",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.on_event("startup")
async def startup_event():
    try:
        # Drop all tables first (for development only)
        # Base.metadata.drop_all(bind=engine)
        # print("🗑️  Dropped all tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"✅ Database tables created successfully for {settings.APP_NAME}")
        
        # Wait a moment to ensure tables are created
        import time
        time.sleep(1)
        
        # Create default admin if not exists
        from app.database import SessionLocal
        from app.crud.crud_admin import crud_admin
        
        db = SessionLocal()
        try:
            # First, let's check if admins table exists by counting
            try:
                admin_count = db.query(Admin).count()
                print(f"📊 Found {admin_count} admins in database")
            except Exception as e:
                print(f"❌ Error querying admins table: {e}")
                # If table doesn't exist, create it manually
                Base.metadata.create_all(bind=engine, tables=[Admin.__table__])
                print("✅ Created admins table manually")
            
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
            print(f"❌ Error creating default admin: {e}")
            # Try to create the admin table specifically
            try:
                Base.metadata.create_all(bind=engine, tables=[Admin.__table__])
                print("✅ Created admins table after error")
            except Exception as table_error:
                print(f"❌ Failed to create admins table: {table_error}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )