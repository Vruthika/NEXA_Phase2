from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.plan_crud import PlanCRUD
from app.crud.category_crud import CategoryCRUD
from app.schemas.plan import PlanCreate, PlanUpdate

class PlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_crud = PlanCRUD(db)
        self.category_crud = CategoryCRUD(db)
    
    def create_plan(self, plan_data: PlanCreate):
        # Check if category exists
        category = self.category_crud.get_by_id(plan_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return self.plan_crud.create(plan_data.dict())
    
    def get_plan_by_id(self, plan_id: int):
        plan = self.plan_crud.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return plan
    
    def get_all_plans(self, skip: int = 0, limit: int = 100):
        return self.plan_crud.get_all(skip, limit)
    
    def get_prepaid_plans(self):
        return self.plan_crud.get_by_type("prepaid")
    
    def get_postpaid_plans(self):
        return self.plan_crud.get_by_type("postpaid")
    
    def get_topup_plans(self):
        return self.plan_crud.get_topup_plans()
    
    def update_plan(self, plan_id: int, plan_data: PlanUpdate):
        plan = self.get_plan_by_id(plan_id)
        return self.plan_crud.update(plan_id, plan_data.dict(exclude_unset=True))
    
    def delete_plan(self, plan_id: int):
        plan = self.get_plan_by_id(plan_id)
        return self.plan_crud.soft_delete(plan_id)
    
    def get_featured_plans(self):
        return self.plan_crud.get_featured_plans()