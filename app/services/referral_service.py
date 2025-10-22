from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import secrets
import string
from app.crud.referral_program_crud import ReferralProgramCRUD
from app.crud.referral_discount_crud import ReferralDiscountCRUD
from app.crud.referral_usage_log_crud import ReferralUsageLogCRUD
from app.crud.customer_crud import CustomerCRUD
from app.schemas.referral_program import ReferralProgramCreate
from app.websockets import websocket_manager

class ReferralService:
    def __init__(self, db: Session):
        self.db = db
        self.referral_crud = ReferralProgramCRUD(db)
        self.discount_crud = ReferralDiscountCRUD(db)
        self.usage_log_crud = ReferralUsageLogCRUD(db)
        self.customer_crud = CustomerCRUD(db)
    
    def generate_referral_code(self, length: int = 8):
        """Generate a random referral code"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_referral(self, referrer_customer_id: int, referee_phone_number: str, max_uses: int = 1):
        # Verify referrer exists
        referrer = self.customer_crud.get_by_id(referrer_customer_id)
        if not referrer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referrer customer not found"
            )
        
        # Check if referral already exists for this phone number
        existing_referral = self.referral_crud.get_by_phone_number(referee_phone_number)
        if existing_referral:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral already exists for this phone number"
            )
        
        # Generate unique referral code
        referral_code = self.generate_referral_code()
        while self.referral_crud.get_by_code(referral_code):
            referral_code = self.generate_referral_code()
        
        # Set expiry date (30 days from now)
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Create referral
        referral_data = {
            "referrer_customer_id": referrer_customer_id,
            "referee_phone_number": referee_phone_number,
            "referral_code": referral_code,
            "max_uses": max_uses,
            "expires_at": expires_at
        }
        
        referral = self.referral_crud.create(referral_data)
        
        return referral
    
    def use_referral_code(self, referral_code: str, used_by_phone: str, used_by_customer_id: int = None):
        # Get referral by code
        referral = self.referral_crud.get_by_code(referral_code)
        if not referral:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid referral code"
            )
        
        # Check if referral is active and not expired
        if not referral.is_active or referral.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral code is expired or inactive"
            )
        
        # Check if max uses reached
        if referral.current_uses >= referral.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral code has reached maximum uses"
            )
        
        # Check if phone number matches
        if referral.referee_phone_number != used_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Referral code is not valid for this phone number"
            )
        
        # Create usage log
        usage_log_data = {
            "referral_id": referral.referral_id,
            "used_by_phone": used_by_phone,
            "used_by_customer_id": used_by_customer_id
        }
        self.usage_log_crud.create(usage_log_data)
        
        # Update referral usage count
        referral.current_uses += 1
        
        # Create discount for referrer
        discount_data = {
            "referral_id": referral.referral_id,
            "customer_id": referral.referrer_customer_id,
            "valid_until": datetime.utcnow() + timedelta(days=90)  # 90 days validity
        }
        discount = self.discount_crud.create(discount_data)
        
        # If this was the last use, mark referral as completed
        if referral.current_uses >= referral.max_uses:
            referral.status = "completed"
            referral.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Send notifications
        try:
            # Notify referrer
            websocket_manager.send_notification(
                referral.referrer_customer_id,
                {
                    "type": "referral_bonus",
                    "message": f"Your referral code was used by {used_by_phone}",
                    "discount_percentage": float(discount.discount_percentage)
                }
            )
            
            # Notify referee if they have an account
            if used_by_customer_id:
                websocket_manager.send_notification(
                    used_by_customer_id,
                    {
                        "type": "referral_bonus",
                        "message": "You have received a referral discount",
                        "discount_percentage": 10.0  # Default for referee
                    }
                )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return {
            "referral": referral,
            "discount": discount
        }
    
    def get_customer_referrals(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return self.referral_crud.get_by_referrer_id(customer_id)
    
    def get_customer_discounts(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return self.discount_crud.get_by_customer_id(customer_id)
    
    def apply_referral_discount(self, discount_id: int, customer_id: int):
        discount = self.discount_crud.get_by_id(discount_id)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount not found"
            )
        
        # Verify discount belongs to customer
        if discount.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this discount"
            )
        
        # Check if discount is valid and not used
        if discount.is_used or discount.valid_until < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount is already used or expired"
            )
        
        # Mark discount as used
        discount.is_used = True
        discount.used_at = datetime.utcnow()
        self.db.commit()
        
        return discount
    
    def get_referral_stats(self, customer_id: int):
        referrals = self.get_customer_referrals(customer_id)
        completed_count = sum(1 for r in referrals if r.status == "completed")
        pending_count = sum(1 for r in referrals if r.status == "pending")
        total_earnings = sum(
            float(discount.discount_percentage) for discount in self.get_customer_discounts(customer_id)
        )
        
        return {
            "total_referrals": len(referrals),
            "completed_referrals": completed_count,
            "pending_referrals": pending_count,
            "total_earnings": total_earnings
        }