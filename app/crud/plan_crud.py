from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.plan import Plan, PlanType, PlanStatus
from app.schemas.plan import PlanCreate, PlanUpdate
from datetime import datetime

class PlanCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, plan_id: int) -> Plan:
        return self.db.query(Plan).filter(Plan.plan_id == plan_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Plan).filter(Plan.deleted_at.is_(None)).offset(skip).limit(limit).all()
    
    def get_by_type(self, plan_type: str):
        return self.db.query(Plan).filter(
            and_(
                Plan.plan_type == plan_type,
                Plan.deleted_at.is_(None)
            )
        ).all()
    
    def get_topup_plans(self):
        return self.db.query(Plan).filter(
            and_(
                Plan.is_topup == True,
                Plan.deleted_at.is_(None)
            )
        ).all()
    
    def get_featured_plans(self):
        return self.db.query(Plan).filter(
            and_(
                Plan.is_featured == True,
                Plan.deleted_at.is_(None),
                Plan.status == PlanStatus.ACTIVE
            )
        ).all()
    
    def get_active_plans(self):
        return self.db.query(Plan).filter(
            and_(
                Plan.status == PlanStatus.ACTIVE,
                Plan.deleted_at.is_(None)
            )
        ).all()
    
    def create(self, plan_data: dict) -> Plan:
        plan = Plan(**plan_data)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def update(self, plan_id: int, plan_data: dict) -> Plan:
        plan = self.get_by_id(plan_id)
        if plan:
            for key, value in plan_data.items():
                setattr(plan, key, value)
            self.db.commit()
            self.db.refresh(plan)
        return plan
    
    def soft_delete(self, plan_id: int) -> Plan:
        plan = self.get_by_id(plan_id)
        if plan:
            plan.deleted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(plan)
        return plan