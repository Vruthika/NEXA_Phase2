from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import random
import string
from typing import List, Optional
from app.models.models import ReferralProgram, ReferralDiscount, ReferralUsageLog, Customer, ReferralStatus
from app.schemas.referral import ReferralProgramCreate
from app.services.automated_notifications import automated_notifications

class CRUDReferral:
    def generate_referral_code(self, db: Session, length=8):
        """Generate a unique referral code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            existing = db.query(ReferralProgram).filter(ReferralProgram.referral_code == code).first()
            if not existing:
                return code

    def get_referral_by_code(self, db: Session, referral_code: str):
        return db.query(ReferralProgram).filter(ReferralProgram.referral_code == referral_code).first()

    def get_referral_by_customer(self, db: Session, customer_id: int):
        """Get active referral program for a customer"""
        return db.query(ReferralProgram).filter(
            ReferralProgram.referrer_customer_id == customer_id,
            ReferralProgram.is_active == True
        ).first()

    def create_referral_program(self, db: Session, customer_id: int):
        """Create a new referral program for a customer"""
        # Check if customer already has an active referral program
        existing = self.get_referral_by_customer(db, customer_id)
        if existing:
            return None, "Customer already has an active referral program"

        referral_code = self.generate_referral_code(db)
        expires_at = datetime.utcnow() + timedelta(days=30)

        referral_program = ReferralProgram(
            referrer_customer_id=customer_id,
            referee_phone_number="",  # Will be set when used
            referral_code=referral_code,
            status=ReferralStatus.pending,
            is_active=True,
            expires_at=expires_at,
            max_uses=1,
            current_uses=0
        )

        db.add(referral_program)
        db.commit()
        db.refresh(referral_program)
        return referral_program, None

    def use_referral_code(self, db: Session, referral_code: str, referee_customer_id: int, referee_phone_number: str):
        """Use a referral code"""
        referral_program = self.get_referral_by_code(db, referral_code)
        if not referral_program:
            return None, "Invalid referral code"

        # Check if referral program is active and not expired
        if not referral_program.is_active:
            return None, "Referral program is not active"

        if referral_program.expires_at < datetime.utcnow():
            referral_program.is_active = False
            referral_program.status = ReferralStatus.expired
            db.commit()
            return None, "Referral code has expired"

        # Check if the code has reached maximum uses
        if referral_program.current_uses >= referral_program.max_uses:
            referral_program.is_active = False
            db.commit()
            return None, "Referral code has reached maximum uses"

        # Check if trying to use own code
        referrer_customer = db.query(Customer).filter(
            Customer.customer_id == referral_program.referrer_customer_id
        ).first()
        
        if referrer_customer and referrer_customer.phone_number == referee_phone_number:
            return None, "Cannot use your own referral code"

        # Check if this phone number has already used this referral code
        existing_usage = db.query(ReferralUsageLog).filter(
            ReferralUsageLog.referral_id == referral_program.referral_id,
            ReferralUsageLog.used_by_phone == referee_phone_number
        ).first()
        if existing_usage:
            return None, "This phone number has already used this referral code"

        # Update referee phone number in referral program
        referral_program.referee_phone_number = referee_phone_number
        referral_program.referee_customer_id = referee_customer_id  # Set referee customer ID immediately

        # Create referral usage log 
        usage_log = ReferralUsageLog(
            referral_id=referral_program.referral_id,
            used_by_phone=referee_phone_number,
            used_by_customer_id=referee_customer_id
        )

        # Create 10% discount for referee that will be used on first recharge
        referee_discount = ReferralDiscount(
            referral_id=referral_program.referral_id,
            customer_id=referee_customer_id,
            discount_percentage=10.00,  # 10% discount for referee
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        db.add(referee_discount)

        db.add(usage_log)
        db.commit()

        return referral_program, None
    
    def complete_referral(self, db: Session, referee_customer_id: int, referee_phone_number: str):
        """Complete referral when referee does first recharge """
        # Find referral program for this referee
        referral_program = db.query(ReferralProgram).filter(
            ReferralProgram.referee_phone_number == referee_phone_number,
            ReferralProgram.status == ReferralStatus.pending
        ).first()

        if not referral_program:
            return None, "No pending referral found for this phone number"

        # Update current uses and check if max uses reached
        referral_program.current_uses += 1
        referral_program.status = ReferralStatus.completed
        referral_program.completed_at = datetime.utcnow()

        if referral_program.current_uses >= referral_program.max_uses:
            referral_program.is_active = False

        # Create 30% discount for referrer
        referrer_discount = ReferralDiscount(
            referral_id=referral_program.referral_id,
            customer_id=referral_program.referrer_customer_id,
            discount_percentage=30.00,  # 30% discount for referrer
            valid_until=datetime.utcnow() + timedelta(days=30)
        )

        db.add(referrer_discount)
        
        # Trigger referral bonus notification for the referrer
        automated_notifications.trigger_referral_bonus_notification(
            db, referral_program.referrer_customer_id, 30.0
        )
        db.commit()

        return referral_program, None
    
    def get_customer_referral_discounts(self, db: Session, customer_id: int):
        """Get all active referral discounts for a customer"""
        return db.query(ReferralDiscount).filter(
            ReferralDiscount.customer_id == customer_id,
            ReferralDiscount.is_used == False,
            ReferralDiscount.valid_until >= datetime.utcnow()
        ).all()

    def mark_discount_used(self, db: Session, discount_id: int, customer_id: int):
        """Mark a referral discount as used"""
        discount = db.query(ReferralDiscount).filter(
            ReferralDiscount.discount_id == discount_id,
            ReferralDiscount.customer_id == customer_id,
            ReferralDiscount.is_used == False
        ).first()

        if discount:
            discount.is_used = True
            discount.used_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_referral_stats(self, db: Session, customer_id: int):
        """Get referral statistics for a customer"""
        referral_program = self.get_referral_by_customer(db, customer_id)
        if not referral_program:
            return None

        # Count successful referrals
        successful_referrals = db.query(ReferralUsageLog).filter(
            ReferralUsageLog.referral_id == referral_program.referral_id,
            ReferralUsageLog.used_by_customer_id.isnot(None)
        ).count()

        return {
            "referral_code": referral_program.referral_code,
            "total_uses": referral_program.current_uses,
            "successful_referrals": successful_referrals,
            "max_uses": referral_program.max_uses,
            "expires_at": referral_program.expires_at,
            "is_active": referral_program.is_active,
            "status": referral_program.status
        }

    def get_all_referral_programs(self, db: Session, skip: int = 0, limit: int = 100, 
                                status: Optional[ReferralStatus] = None, 
                                is_active: Optional[bool] = None):
        """Get all referral programs (for admin)"""
        query = db.query(ReferralProgram)
        
        if status:
            query = query.filter(ReferralProgram.status == status)
        if is_active is not None:
            query = query.filter(ReferralProgram.is_active == is_active)
            
        return query.order_by(ReferralProgram.created_at.desc()).offset(skip).limit(limit).all()

    def get_referral_usage_logs(self, db: Session, referral_id: int):
        """Get usage logs for a referral program"""
        return db.query(ReferralUsageLog).filter(
            ReferralUsageLog.referral_id == referral_id
        ).all()

    def get_system_referral_stats(self, db: Session):
        """Get system-wide referral statistics (for admin)"""
        total_referral_programs = db.query(ReferralProgram).count()
        active_referral_programs = db.query(ReferralProgram).filter(ReferralProgram.is_active == True).count()
        total_referral_uses = db.query(func.sum(ReferralProgram.current_uses)).scalar() or 0
        
        status_counts = db.query(
            ReferralProgram.status,
            func.count(ReferralProgram.referral_id)
        ).group_by(ReferralProgram.status).all()
        
        status_stats = {status.value: count for status, count in status_counts}

        # Get top referrers
        top_referrers = db.query(
            ReferralProgram.referrer_customer_id,
            func.count(ReferralUsageLog.log_id).label('referral_count')
        ).join(
            ReferralUsageLog, ReferralProgram.referral_id == ReferralUsageLog.referral_id
        ).group_by(
            ReferralProgram.referrer_customer_id
        ).order_by(
            func.count(ReferralUsageLog.log_id).desc()
        ).limit(10).all()

        top_referrers_details = []
        for referrer in top_referrers:
            customer = db.query(Customer).filter(Customer.customer_id == referrer.referrer_customer_id).first()
            if customer:
                top_referrers_details.append({
                    "customer_id": customer.customer_id,
                    "customer_name": customer.full_name,
                    "phone_number": customer.phone_number,
                    "referral_count": referrer.referral_count
                })

        return {
            "total_referral_programs": total_referral_programs,
            "active_referral_programs": active_referral_programs,
            "total_referral_uses": total_referral_uses,
            "status_stats": status_stats,
            "top_referrers": top_referrers_details
        }

crud_referral = CRUDReferral()