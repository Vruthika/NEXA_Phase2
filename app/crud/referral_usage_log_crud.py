from sqlalchemy.orm import Session
from app.models.referral_usage_log import ReferralUsageLog

class ReferralUsageLogCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, log_id: int) -> ReferralUsageLog:
        return self.db.query(ReferralUsageLog).filter(ReferralUsageLog.log_id == log_id).first()
    
    def get_by_referral_id(self, referral_id: int):
        return self.db.query(ReferralUsageLog).filter(ReferralUsageLog.referral_id == referral_id).all()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(ReferralUsageLog).filter(ReferralUsageLog.used_by_customer_id == customer_id).all()
    
    def create(self, log_data: dict) -> ReferralUsageLog:
        log = ReferralUsageLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_usage_count(self, referral_id: int):
        return self.db.query(ReferralUsageLog).filter(ReferralUsageLog.referral_id == referral_id).count()