from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.crud.transaction_crud import TransactionCRUD
from app.crud.plan_crud import PlanCRUD
from app.crud.offer_crud import OfferCRUD
from app.crud.customer_crud import CustomerCRUD
from app.schemas.transaction import TransactionCreate
from app.utils.payment_gateway import process_payment
from app.utils.sms_service import send_sms
from app.websockets import websocket_manager

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_crud = TransactionCRUD(db)
        self.plan_crud = PlanCRUD(db)
        self.offer_crud = OfferCRUD(db)
        self.customer_crud = CustomerCRUD(db)
    
    def create_transaction(self, customer_id: int, transaction_data: TransactionCreate):
        # Verify customer exists
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify plan exists
        plan = self.plan_crud.get_by_id(transaction_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Calculate amounts
        original_amount = plan.price
        discount_amount = 0
        final_amount = original_amount
        
        # Apply offer if provided
        if transaction_data.offer_id:
            offer = self.offer_crud.get_by_id(transaction_data.offer_id)
            if offer and offer.is_valid():
                discount_amount = float(original_amount) - float(offer.discounted_price)
                final_amount = offer.discounted_price
        
        # Process payment
        payment_result = process_payment(
            amount=float(final_amount),
            payment_method=transaction_data.payment_method
        )
        
        if payment_result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment failed: {payment_result.get('message', 'Unknown error')}"
            )
        
        # Create transaction record
        transaction_dict = transaction_data.dict()
        transaction_dict.update({
            "customer_id": customer_id,
            "original_amount": original_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "payment_status": "success",
            "transaction_date": datetime.utcnow()
        })
        
        transaction = self.transaction_crud.create(transaction_dict)
        
        # Send SMS notification
        try:
            send_sms(
                to=transaction_data.recipient_phone_number,
                message=f"Your recharge of ₹{final_amount} was successful. Thank you for using NEXA!"
            )
        except Exception as e:
            # Log SMS failure but don't fail the transaction
            print(f"SMS sending failed: {e}")
        
        # Send WebSocket notification
        try:
            websocket_manager.send_transaction_update(
                customer_id,
                {
                    "transaction_id": transaction.transaction_id,
                    "status": "success",
                    "amount": float(final_amount),
                    "plan_name": plan.plan_name
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return transaction
    
    def get_transaction_by_id(self, transaction_id: int):
        transaction = self.transaction_crud.get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
    
    def get_customer_transactions(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.transaction_crud.get_by_customer_id(customer_id)