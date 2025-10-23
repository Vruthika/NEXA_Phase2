from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routes import admin, auth

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