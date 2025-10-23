from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from app.database import get_db
from app.models.models import Admin, Customer, Transaction
from app.schemas.admin import *
from app.core.auth import get_current_admin
from app.crud import crud_admin, crud_category, crud_plan
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate

# ==========================================================
# 🧑‍💼 ADMIN MANAGEMENT ROUTES
# ==========================================================
admin_router = APIRouter(prefix="/admins", tags=["Admin Management"])

@admin_router.post("/", response_model=AdminResponse)
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

@admin_router.get("/", response_model=List[AdminResponse])
async def get_all_admins(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_admin.get_all(db)

@admin_router.get("/{admin_id}", response_model=AdminResponse)
async def get_admin(
    admin_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.get_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin

@admin_router.put("/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.update(db, admin_id, admin_data)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin

@admin_router.post("/change-password")
async def change_password(
    password_data: AdminChangePassword,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not crud_admin.authenticate(db, current_admin.email, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    crud_admin.change_password(db, current_admin.admin_id, password_data.new_password)
    return {"message": "Password changed successfully"}


# ==========================================================
# 🏷️ CATEGORY MANAGEMENT ROUTES
# ==========================================================
category_router = APIRouter(prefix="/categories", tags=["Category Management"])

@category_router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.create(db, category_data)

@category_router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.get_all(db)

@category_router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.update(db, category_id, category_data.category_name)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@category_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.delete(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"message": "Category deleted successfully"}


# ==========================================================
# 📦 PLAN MANAGEMENT ROUTES
# ==========================================================
plan_router = APIRouter(prefix="/plans", tags=["Plan Management"])

@plan_router.post("/", response_model=PlanResponse)
async def create_plan(
    plan_data: PlanCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.create(db, plan_data)

@plan_router.get("/", response_model=List[PlanResponse])
async def get_plans(
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.get_all(db, plan_type=plan_type, category_id=category_id, status=status)

@plan_router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.get(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@plan_router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.update(db, plan_id, plan_data)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@plan_router.post("/{plan_id}/activate", response_model=PlanResponse)
async def activate_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.activate(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@plan_router.post("/{plan_id}/deactivate", response_model=PlanResponse)
async def deactivate_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.deactivate(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@plan_router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.delete(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return {"message": "Plan deleted successfully"}


# ==========================================================
# 📊 DASHBOARD ANALYTICS ROUTES
# ==========================================================
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])

@dashboard_router.get("/")
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.account_status == "active").count()
    total_transactions = db.query(Transaction).count()

    today = datetime.utcnow().date()
    todays_transactions = db.query(Transaction).filter(
        func.date(Transaction.transaction_date) == today
    ).count()

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