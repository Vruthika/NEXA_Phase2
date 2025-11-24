from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import (
    PostpaidActivation, PostpaidSecondaryNumber, 
    PostpaidDataAddon, Customer, Plan, Transaction,
    PostpaidStatus, AddonStatus
)
from app.schemas.postpaid import PostpaidActivationFilter

class CRUDPostpaid:
    # ==========================================================
    # POSTPAID ACTIVATION METHODS
    # ==========================================================
    
    def get_activation_by_id(self, db: Session, activation_id: int):
        return db.query(PostpaidActivation).filter(
            PostpaidActivation.activation_id == activation_id
        ).first()
    
    def get_activation_by_customer(self, db: Session, customer_id: int):
        """Get current active postpaid activation where customer is primary owner"""
        return db.query(PostpaidActivation).filter(
            PostpaidActivation.customer_id == customer_id,
            PostpaidActivation.status == PostpaidStatus.active
        ).first()
        
    def get_activation_by_secondary_customer(self, db: Session, customer_id: int):
        """Get current active postpaid activation where customer is secondary number"""
        return db.query(PostpaidActivation).join(
            PostpaidSecondaryNumber,
            PostpaidActivation.activation_id == PostpaidSecondaryNumber.activation_id
        ).filter(
            PostpaidSecondaryNumber.customer_id == customer_id,
            PostpaidActivation.status == PostpaidStatus.active
        ).first()
    
    def get_activation_by_primary_number(self, db: Session, primary_number: str):
        """Get current active postpaid activation by primary phone number"""
        return db.query(PostpaidActivation).filter(
            PostpaidActivation.primary_number == primary_number,
            PostpaidActivation.status == PostpaidStatus.active
        ).first()
    
    def get_all_activations(
        self, 
        db: Session, 
        filter: PostpaidActivationFilter,
        skip: int = 0, 
        limit: int = 100
    ):
        """Get all postpaid activations (including completed ones)"""
        query = db.query(PostpaidActivation).join(
            Customer, PostpaidActivation.customer_id == Customer.customer_id
        ).join(
            Plan, PostpaidActivation.plan_id == Plan.plan_id
        )
        
        # Apply filters
        if filter.plan_id:
            query = query.filter(PostpaidActivation.plan_id == filter.plan_id)
        
        if filter.status:
            query = query.filter(PostpaidActivation.status == filter.status)
        
        if filter.customer_phone:
            query = query.filter(
                or_(
                    PostpaidActivation.primary_number.ilike(f"%{filter.customer_phone}%"),
                    Customer.phone_number.ilike(f"%{filter.customer_phone}%")
                )
            )
        
        if filter.date_from:
            query = query.filter(PostpaidActivation.created_at >= filter.date_from)
        
        if filter.date_to:
            end_date = filter.date_to + timedelta(days=1)
            query = query.filter(PostpaidActivation.created_at < end_date)
        
        return query.order_by(PostpaidActivation.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_activations_for_customer(self, db: Session, customer_id: int, customer_phone: str = None):
        """Get all active postpaid activations for customer (both primary and secondary)"""
        
        # Always get customer phone from database to ensure it's available
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            print(f"DEBUG: Customer with ID {customer_id} not found")
            return []
        
        # Use provided phone or get from customer record
        phone_to_use = customer_phone or customer.phone_number
        
        print(f"DEBUG: Searching activations for customer_id: {customer_id}, phone: {phone_to_use}")
        
        # Get activations where customer is primary owner
        primary_activations = db.query(PostpaidActivation).filter(
            PostpaidActivation.customer_id == customer_id,
            PostpaidActivation.status == PostpaidStatus.active
        ).all()

        print(f"DEBUG: Found {len(primary_activations)} primary activations")

        # Get activations where customer is linked as secondary number by customer_id
        secondary_activations_by_customer_id = db.query(PostpaidActivation).join(
            PostpaidSecondaryNumber,
            PostpaidActivation.activation_id == PostpaidSecondaryNumber.activation_id
        ).filter(
            PostpaidSecondaryNumber.customer_id == customer_id,
            PostpaidActivation.status == PostpaidStatus.active
        ).all()

        print(f"DEBUG: Found {len(secondary_activations_by_customer_id)} secondary activations by customer_id")

        # get activations where the phone number matches (even if customer_id is not set)
        secondary_activations_by_phone = db.query(PostpaidActivation).join(
            PostpaidSecondaryNumber,
            PostpaidActivation.activation_id == PostpaidSecondaryNumber.activation_id
        ).filter(
            PostpaidSecondaryNumber.phone_number == phone_to_use,
            PostpaidActivation.status == PostpaidStatus.active
        ).all()

        print(f"DEBUG: Found {len(secondary_activations_by_phone)} secondary activations by phone")

        # Combine all activations
        all_activations = primary_activations + secondary_activations_by_customer_id + secondary_activations_by_phone
        
        # Remove duplicates by activation_id
        seen = set()
        unique_activations = []
        for activation in all_activations:
            if activation.activation_id not in seen:
                seen.add(activation.activation_id)
                unique_activations.append(activation)
        
        print(f"DEBUG: Total unique activations: {len(unique_activations)}")
        return unique_activations
    
    def create_activation(self, db: Session, customer_id: int, plan_id: int, primary_number: str):
        print(f"DEBUG: Creating postpaid activation for customer {customer_id}, plan {plan_id}, number {primary_number}")
        
        try:
            # Check if the primary phone number already has an active postpaid activation
            existing_activation = self.get_activation_by_primary_number(db, primary_number)
            if existing_activation:
                print(f"DEBUG: Primary number {primary_number} already has active postpaid activation {existing_activation.activation_id}")
                return None, f"Phone number {primary_number} already has an active postpaid plan. Only one postpaid plan is allowed per phone number."
            
            # Get plan details
            plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
            if not plan:
                print(f"DEBUG: Plan {plan_id} not found")
                return None, "Plan not found"
            
            print(f"DEBUG: Found plan - ID: {plan.plan_id}, Name: {plan.plan_name}, Type: {plan.plan_type}")
            
            # Fix: Make the comparison case-insensitive
            if plan.plan_type.lower() != "postpaid":
                print(f"DEBUG: Plan {plan_id} is not postpaid, it's {plan.plan_type}")
                return None, "Selected plan is not a postpaid plan"
            
            current_time = datetime.utcnow()
            billing_cycle_end = current_time + timedelta(days=30)
            
            print(f"DEBUG: Creating activation with billing cycle: {current_time} to {billing_cycle_end}")
            
            # Convert to Decimal for database fields
            from decimal import Decimal
            base_data_allowance = Decimal(str(plan.data_allowance_gb)) if plan.data_allowance_gb else Decimal('0.0')
            base_amount = Decimal(str(plan.price))
            
            activation = PostpaidActivation(
                customer_id=customer_id,
                plan_id=plan_id,
                primary_number=primary_number,
                billing_cycle_start=current_time,
                billing_cycle_end=billing_cycle_end,
                base_data_allowance_gb=base_data_allowance,
                current_data_balance_gb=base_data_allowance,
                data_used_gb=Decimal('0.0'),
                base_amount=base_amount,
                total_amount_due=base_amount,
                status=PostpaidStatus.active
            )
            
            db.add(activation)
            db.commit()
            db.refresh(activation)
            print(f"DEBUG: Successfully created postpaid activation {activation.activation_id}")
            return activation, None
            
        except Exception as e:
            db.rollback()
            print(f"DEBUG: Error creating postpaid activation: {str(e)}")
            return None, f"Database error: {str(e)}"
    
    # ==========================================================
    # BILLING METHODS
    # ==========================================================
    
    def get_bill_details(self, db: Session, activation_id: int):
        activation = self.get_activation_by_id(db, activation_id)
        if not activation:
            return None
        
        # Calculate addon charges
        addon_charges = db.query(func.sum(PostpaidDataAddon.addon_price)).filter(
            PostpaidDataAddon.activation_id == activation_id,
            PostpaidDataAddon.status == AddonStatus.active
        ).scalar() or 0.0
        
        return {
            "activation": activation,
            "addon_charges": float(addon_charges),
            "total_amount_due": float(activation.total_amount_due)
        }
    
    def process_bill_payment(self, db: Session, activation_id: int, payment_method: str):
        activation = self.get_activation_by_id(db, activation_id)
        if not activation:
            return None, "Activation not found"
        
        current_time = datetime.utcnow()
        
        # Check if payment is allowed (only at or after billing cycle end)
        if current_time < activation.billing_cycle_end:
            return None, f"Bill payment is only allowed after the billing cycle ends on {activation.billing_cycle_end.strftime('%Y-%m-%d')}"
        
        # Check if bill is already paid
        if activation.total_amount_due <= 0:
            return None, "No outstanding bill amount to pay"
        
        # Create transaction
        transaction = Transaction(
            customer_id=activation.customer_id,
            plan_id=activation.plan_id,
            recipient_phone_number=activation.primary_number,
            transaction_type="postpaid_bill_payment",
            original_amount=activation.total_amount_due,
            discount_amount=0.0,
            final_amount=activation.total_amount_due,
            payment_method=payment_method,
            payment_status="success"
        )
        
        db.add(transaction)
        
        # Mark activation as completed and remove it from active status
        activation.status = PostpaidStatus.cancelled
        activation.total_amount_due = 0.0
        
        # Mark all active addons as expired
        db.query(PostpaidDataAddon).filter(
            PostpaidDataAddon.activation_id == activation_id,
            PostpaidDataAddon.status == AddonStatus.active
        ).update({
            PostpaidDataAddon.status: AddonStatus.expired
        })
        
        db.commit()
        return transaction, None
    
    def get_due_payments(self, db: Session):
        """Get activations with due payments (only unpaid bills)"""
        return db.query(PostpaidActivation).filter(
            PostpaidActivation.status == PostpaidStatus.active,
            PostpaidActivation.total_amount_due > 0
        ).all()
    
    # ==========================================================
    # DATA ADDON METHODS
    # ==========================================================
    
    def purchase_data_addon(self, db: Session, activation_id: int, addon_name: str, 
                      data_amount_gb: float, addon_price: float):
        activation = self.get_activation_by_id(db, activation_id)
        if not activation:
            return None
        
        current_time = datetime.utcnow()
        
        valid_until = activation.billing_cycle_end
        
        from decimal import Decimal
        data_amount_gb_decimal = Decimal(str(data_amount_gb))
        addon_price_decimal = Decimal(str(addon_price))
        
        addon = PostpaidDataAddon(
            activation_id=activation_id,
            addon_name=addon_name,
            data_amount_gb=data_amount_gb_decimal,
            addon_price=addon_price_decimal,
            valid_until=valid_until,
            status=AddonStatus.active
        )
        
        # Update data balance and total amount due - using Decimal arithmetic
        activation.current_data_balance_gb += data_amount_gb_decimal
        activation.total_amount_due += addon_price_decimal
        
        db.add(addon)
        db.commit()
        db.refresh(addon)
        return addon
    
    def get_active_addons(self, db: Session, activation_id: int):
        return db.query(PostpaidDataAddon).filter(
            PostpaidDataAddon.activation_id == activation_id,
            PostpaidDataAddon.status == AddonStatus.active
        ).all()
    
    # ==========================================================
    # SECONDARY NUMBER METHODS
    # ==========================================================
    
    def add_secondary_number(self, db: Session, activation_id: int, phone_number: str, customer_id: int = None):
        """
        Add a secondary number to postpaid activation.
        Returns: secondary_number_object or None
        """
        try:
            activation = self.get_activation_by_id(db, activation_id)
            if not activation:
                print(f"DEBUG: Activation {activation_id} not found")
                return None
            
            # Get plan details to check if secondary numbers are allowed
            plan = db.query(Plan).filter(Plan.plan_id == activation.plan_id).first()
            if not plan:
                print(f"DEBUG: Plan for activation {activation_id} not found")
                return None
            
            # Check if plan supports secondary numbers
            if getattr(plan, 'max_secondary_numbers', 0) == 0:
                print(f"DEBUG: Plan {plan.plan_id} does not support secondary numbers (max_secondary_numbers = {getattr(plan, 'max_secondary_numbers', 0)})")
                return None
            
            # Check current secondary number count
            current_secondary_count = db.query(PostpaidSecondaryNumber).filter(
                PostpaidSecondaryNumber.activation_id == activation_id
            ).count()
            
            # Check if maximum limit reached
            max_allowed = getattr(plan, 'max_secondary_numbers', 0)
            if current_secondary_count >= max_allowed:
                print(f"DEBUG: Maximum secondary numbers ({max_allowed}) reached for activation {activation_id}")
                return None
            
            # Check if secondary number already exists
            existing = db.query(PostpaidSecondaryNumber).filter(
                PostpaidSecondaryNumber.activation_id == activation_id,
                PostpaidSecondaryNumber.phone_number == phone_number
            ).first()
            
            if existing:
                print(f"DEBUG: Secondary number {phone_number} already exists for activation {activation_id}")
                return None
            
            secondary = PostpaidSecondaryNumber(
                activation_id=activation_id,
                phone_number=phone_number,
                customer_id=customer_id
            )
            
            db.add(secondary)
            db.commit()
            db.refresh(secondary)
            print(f"DEBUG: Successfully added secondary number {secondary.secondary_id}")
            return secondary
            
        except Exception as e:
            db.rollback()
            print(f"DEBUG: Error adding secondary number: {str(e)}")
            return None
    
    def remove_secondary_number(self, db: Session, secondary_id: int):
        secondary = db.query(PostpaidSecondaryNumber).filter(
            PostpaidSecondaryNumber.secondary_id == secondary_id
        ).first()
        
        if secondary:
            db.delete(secondary)
            db.commit()
        return secondary
    
    def get_secondary_numbers(self, db: Session, activation_id: int):
        return db.query(PostpaidSecondaryNumber).filter(
            PostpaidSecondaryNumber.activation_id == activation_id
        ).all()
    
    # ==========================================================
    # DATA USAGE METHODS
    # ==========================================================
    
    def update_data_usage(self, db: Session, activation_id: int, data_used_gb: float):
        activation = self.get_activation_by_id(db, activation_id)
        if not activation:
            return None
        
        activation.data_used_gb += data_used_gb
        activation.current_data_balance_gb = max(0, activation.current_data_balance_gb - data_used_gb)
        
        db.commit()
        db.refresh(activation)
        return activation

crud_postpaid = CRUDPostpaid()