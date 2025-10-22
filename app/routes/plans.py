from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse
from app.services.plan_service import PlanService

router = APIRouter()

@router.get("/", response_model=List[PlanResponse])
async def get_all_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    plan_service = PlanService(db)
    return plan_service.get_all_plans(skip, limit)

@router.get("/prepaid", response_model=List[PlanResponse])
async def get_prepaid_plans(db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_prepaid_plans()

@router.get("/postpaid", response_model=List[PlanResponse])
async def get_postpaid_plans(db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_postpaid_plans()

@router.get("/topup", response_model=List[PlanResponse])
async def get_topup_plans(db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_topup_plans()

@router.get("/featured", response_model=List[PlanResponse])
async def get_featured_plans(db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_featured_plans()

@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan_by_id(plan_id: int, db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    return plan_service.get_plan_by_id(plan_id)

@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db)
):
    plan_service = PlanService(db)
    return plan_service.create_plan(plan_data)

@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db)
):
    plan_service = PlanService(db)
    return plan_service.update_plan(plan_id, plan_data)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan_service = PlanService(db)
    plan_service.delete_plan(plan_id)
    return None