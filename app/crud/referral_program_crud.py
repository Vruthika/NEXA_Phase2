from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.referral_program import ReferralProgram
from datetime import datetime

class ReferralProgramCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, referral_id: int) -> ReferralProgram:
        return self.db.query(ReferralProgram).filter(ReferralProgram.referral_id == referral_id).first()
    
    def get_by_code(self, referral_code: str) -> ReferralProgram:
        return self.db.query(ReferralProgram).filter(ReferralProgram.referral_code == referral_code).first()
    
    def get_by_phone_number(self, phone_number: str):
        return self.db.query(ReferralProgram).filter(ReferralProgram.referee_phone_number == phone_number).first()
    
    def get_by_referrer_id(self, referrer_customer_id: int):
        return self.db.query(ReferralProgram).filter(ReferralProgram.referrer_customer_id == referrer_customer_id).all()
    
    def get_active_referrals(self):
        return self.db.query(ReferralProgram).filter(
            and_(
                ReferralProgram.is_active == True,
                ReferralProgram.expires_at > datetime.utcnow()
            )
        ).all()
    
    def create(self, referral_data: dict) -> ReferralProgram:
        referral = ReferralProgram(**referral_data)
        self.db.add(referral)
        self.db.commit()
        self.db.refresh(referral)
        return referral
    
    def update(self, referral_id: int, referral_data: dict) -> ReferralProgram:
        referral = self.get_by_id(referral_id)
        if referral:
            for key, value in referral_data.items():
                setattr(referral, key, value)
            self.db.commit()
            self.db.refresh(referral)
        return referral
    
    def increment_uses(self, referral_id: int) -> ReferralProgram:
        referral = self.get_by_id(referral_id)
        if referral:
            referral.current_uses += 1
            self.db.commit()
            self.db.refresh(referral)
        return referral
    
    def deactivate(self, referral_id: int) -> ReferralProgram:
        referral = self.get_by_id(referral_id)
        if referral:
            referral.is_active = False
            self.db.commit()
            self.db.refresh(referral)
        return referral