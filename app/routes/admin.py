from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from app.database import get_db
from app.models.models import Admin, Customer, Transaction  # Import all required models
from app.schemas.admin import *
from app.core.auth import get_current_admin
from app.crud import crud_admin, crud_category, crud_plan
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

router = APIRouter(prefix="/admin", tags=["admin"])

# Admin Management
@router.post("/admins", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing_admin = crud_admin.get_by_email(db, admin_data.email)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud_admin.create(db, admin_data)

@router.get("/admins", response_model=List[AdminResponse])
async def get_all_admins(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_admin.get_all(db)

@router.get("/admins/{admin_id}", response_model=AdminResponse)
async def get_admin(
    admin_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.get_by_id(db, admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return admin

@router.put("/admins/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.update(db, admin_id, admin_data)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return admin

@router.post("/change-password")
async def change_password(
    password_data: AdminChangePassword,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not crud_admin.authenticate(db, current_admin.email, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    crud_admin.change_password(db, current_admin.admin_id, password_data.new_password)
    return {"message": "Password changed successfully"}

# Category Management
@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.create(db, category_data)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.get_all(db)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.update(db, category_id, category_data.category_name)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.delete(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return {"message": "Category deleted successfully"}

# Plan Management
@router.post("/plans", response_model=PlanResponse)
async def create_plan(
    plan_data: PlanCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.create(db, plan_data)

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.get_all(db, plan_type=plan_type, category_id=category_id)

@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.get(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.update(db, plan_id, plan_data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.delete(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return {"message": "Plan deleted successfully"}

# Dashboard Analytics
@router.get("/dashboard")
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Total customers
    total_customers = db.query(Customer).count()
    
    # Active customers
    active_customers = db.query(Customer).filter(
        Customer.account_status == "active"
    ).count()
    
    # Total transactions
    total_transactions = db.query(Transaction).count()
    
    # Today's transactions
    today = datetime.utcnow().date()
    todays_transactions = db.query(Transaction).filter(
        func.date(Transaction.transaction_date) == today
    ).count()
    
    # Total revenue
    total_revenue_result = db.query(func.sum(Transaction.final_amount)).filter(
        Transaction.payment_status == "success"
    ).first()
    total_revenue = float(total_revenue_result[0]) if total_revenue_result[0] else 0.0
    
    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_transactions": total_transactions,
        "todays_transactions": todays_transactions,
        "total_revenue": total_revenue
    }