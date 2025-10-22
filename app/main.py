from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.routes import auth, admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NEXA Admin System", version="1.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)

# Mount static files (make sure 'static' directory exists)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "NEXA Admin System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}