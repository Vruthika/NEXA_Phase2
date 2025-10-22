from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.active_topup import ActiveTopup, TopupStatus
from datetime import datetime

class ActiveTopupCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, topup_id: int) -> ActiveTopup:
        return self.db.query(ActiveTopup).filter(ActiveTopup.topup_id == topup_id).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(ActiveTopup).filter(ActiveTopup.customer_id == customer_id).all()
    
    def get_by_subscription_id(self, subscription_id: int):
        return self.db.query(ActiveTopup).filter(ActiveTopup.base_subscription_id == subscription_id).all()
    
    def get_active_topups(self, customer_id: int):
        return self.db.query(ActiveTopup).filter(
            and_(
                ActiveTopup.customer_id == customer_id,
                ActiveTopup.status == TopupStatus.ACTIVE,
                ActiveTopup.expiry_date > datetime.utcnow()
            )
        ).all()
    
    def create(self, topup_data: dict) -> ActiveTopup:
        topup = ActiveTopup(**topup_data)
        self.db.add(topup)
        self.db.commit()
        self.db.refresh(topup)
        return topup
    
    def update_data_usage(self, topup_id: int, data_used_gb: float) -> ActiveTopup:
        topup = self.get_by_id(topup_id)
        if topup:
            topup.data_remaining_gb -= data_used_gb
            if topup.data_remaining_gb <= 0:
                topup.status = TopupStatus.EXHAUSTED
            self.db.commit()
            self.db.refresh(topup)
        return topup
    
    def update_status(self, topup_id: int, status: TopupStatus) -> ActiveTopup:
        topup = self.get_by_id(topup_id)
        if topup:
            topup.status = status
            self.db.commit()
            self.db.refresh(topup)
        return topup
    
    def expire_topups(self):
        expired_topups = self.db.query(ActiveTopup).filter(
            and_(
                ActiveTopup.expiry_date <= datetime.utcnow(),
                ActiveTopup.status == TopupStatus.ACTIVE
            )
        ).all()
        
        for topup in expired_topups:
            topup.status = TopupStatus.EXPIRED
        
        self.db.commit()
        return expired_topups