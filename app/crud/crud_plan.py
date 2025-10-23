from sqlalchemy.orm import Session
from app.models.models import Plan, PlanStatus
from app.schemas.plan import PlanCreate, PlanUpdate

class CRUDPlan:
    def get(self, db: Session, plan_id: int):
        return db.query(Plan).filter(Plan.plan_id == plan_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, plan_type: str = None, category_id: int = None, status: str = None):
        query = db.query(Plan)
        if plan_type:
            query = query.filter(Plan.plan_type == plan_type)
        if category_id:
            query = query.filter(Plan.category_id == category_id)
        if status:
            query = query.filter(Plan.status == status)
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, plan: PlanCreate):
        db_plan = Plan(**plan.model_dump())
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    def update(self, db: Session, plan_id: int, plan_update: PlanUpdate):
        db_plan = self.get(db, plan_id)
        if db_plan:
            update_data = plan_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_plan, field, value)
            db.commit()
            db.refresh(db_plan)
        return db_plan
    
    def change_status(self, db: Session, plan_id: int, status: PlanStatus):
        db_plan = self.get(db, plan_id)
        if db_plan:
            db_plan.status = status
            db.commit()
            db.refresh(db_plan)
        return db_plan
    
    def activate(self, db: Session, plan_id: int):
        return self.change_status(db, plan_id, PlanStatus.active)
    
    def deactivate(self, db: Session, plan_id: int):
        return self.change_status(db, plan_id, PlanStatus.inactive)
    
    def delete(self, db: Session, plan_id: int):
        from datetime import datetime
        db_plan = self.get(db, plan_id)
        if db_plan:
            db_plan.deleted_at = datetime.utcnow()
            db.commit()
        return db_plan

crud_plan = CRUDPlan()