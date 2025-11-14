from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from app.database import get_db
from app.models.models import Admin, Customer, Offer, Plan, Transaction
from app.schemas.admin import *
from app.core.auth import get_current_admin
from app.crud import crud_admin, crud_category, crud_plan
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.plan import PlanCreate, PlanResponse, PlanUpdate
from app.schemas.offer import DiscountCalculationResponse, OfferCreate, OfferCreateWithDiscount, OfferResponse, OfferStatus, OfferUpdate
from app.crud import crud_offer
from app.schemas.transaction import TransactionResponse, TransactionFilter, TransactionExportRequest
from app.crud import crud_transaction, crud_subscription
from app.models.models import Subscription, SubscriptionActivationQueue
from app.schemas.customer import CustomerResponse, CustomerDetailResponse, CustomerUpdate, CustomerFilter, CustomerStatsResponse
from app.crud import crud_customer
from app.models.models import AccountStatus

import csv
import io
import json

# ==========================================================
# 🧑‍💼 ADMIN MANAGEMENT ROUTES
# ==========================================================
admin_router = APIRouter(prefix="/admins", tags=["Admin Management"])

@admin_router.post("/", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    existing_admin = crud_admin.get_by_email(db, admin_data.email)
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud_admin.create(db, admin_data)

@admin_router.get("/", response_model=List[AdminResponse])
async def get_all_admins(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_admin.get_all(db)

@admin_router.get("/{admin_id}", response_model=AdminResponse)
async def get_admin(
    admin_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.get_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin

@admin_router.put("/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    admin = crud_admin.update(db, admin_id, admin_data)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin

@admin_router.post("/change-password")
async def change_password(
    password_data: AdminChangePassword,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not crud_admin.authenticate(db, current_admin.email, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    crud_admin.change_password(db, current_admin.admin_id, password_data.new_password)
    return {"message": "Password changed successfully"}


# ==========================================================
# 🏷️ CATEGORY MANAGEMENT ROUTES
# ==========================================================
category_router = APIRouter(prefix="/categories", tags=["Category Management"])

@category_router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.create(db, category_data)

@category_router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_category.get_all(db)

@category_router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.update(db, category_id, category_data.category_name)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@category_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    category = crud_category.delete(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"message": "Category deleted successfully"}


# ==========================================================
# 📦 PLAN MANAGEMENT ROUTES
# ==========================================================
plan_router = APIRouter(prefix="/plans", tags=["Plan Management"])

@plan_router.post("/", response_model=PlanResponse)
async def create_plan(
    plan_data: PlanCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.create(db, plan_data)

@plan_router.get("/", response_model=List[PlanResponse])
async def get_plans(
    plan_type: Optional[str] = Query(None, description="Filter by plan type"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return crud_plan.get_all(db, plan_type=plan_type, category_id=category_id, status=status)

@plan_router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.get(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@plan_router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.update(db, plan_id, plan_data)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan

@plan_router.post("/{plan_id}/activate", response_model=PlanResponse)
async def activate_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.activate(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@plan_router.post("/{plan_id}/deactivate", response_model=PlanResponse)
async def deactivate_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.deactivate(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan

@plan_router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = crud_plan.delete(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return {"message": "Plan deleted successfully"}

# ==========================================================
# 🎁 OFFER MANAGEMENT ROUTES
# ==========================================================
offer_router = APIRouter(prefix="/offers", tags=["Offer Management"])

# CREATE OFFER - Direct Price Method
@offer_router.post("/", response_model=OfferResponse)
async def create_offer(
    offer_data: OfferCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new offer by specifying discounted price directly.
    """
    # Check if plan exists
    plan = db.query(Plan).filter(Plan.plan_id == offer_data.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Check if discounted price is valid
    if offer_data.discounted_price >= plan.price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discounted price must be less than original plan price"
        )
    
    offer = crud_offer.create(db, offer_data)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create offer"
        )
    
    # Calculate and add status to response
    offer_status = crud_offer.calculate_offer_status(offer)
    
    # Create response data with proper date formatting
    response_data = {
        "offer_id": offer.offer_id,
        "plan_id": offer.plan_id,
        "offer_name": offer.offer_name,
        "description": offer.description,
        "discounted_price": float(offer.discounted_price),
        "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
        "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
        "status": offer_status,
        "created_at": offer.created_at
    }
    
    return OfferResponse(**response_data)

# CREATE OFFER - Discount Percentage Method
@offer_router.post("/create-with-discount", response_model=OfferResponse)
async def create_offer_with_discount(
    offer_data: OfferCreateWithDiscount,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create an offer by specifying discount percentage.
    The system automatically calculates the discounted price.
    """
    # Check if plan exists
    plan = db.query(Plan).filter(Plan.plan_id == offer_data.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Create offer with discount percentage
    offer = crud_offer.create_with_discount_percentage(db, offer_data)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create offer with discount percentage"
        )
    
    # Calculate and add status to response
    offer_status = crud_offer.calculate_offer_status(offer)
    
    # Create response data with proper date formatting
    response_data = {
        "offer_id": offer.offer_id,
        "plan_id": offer.plan_id,
        "offer_name": offer.offer_name,
        "description": offer.description,
        "discounted_price": float(offer.discounted_price),
        "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
        "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
        "status": offer_status,
        "created_at": offer.created_at
    }
    
    return OfferResponse(**response_data)

# CALCULATE DISCOUNT - Preview Only
@offer_router.get("/calculate-discount", response_model=DiscountCalculationResponse)
async def calculate_discount(
    plan_id: int = Query(..., description="Plan ID"),
    discount_percentage: float = Query(..., description="Discount percentage (0-100)"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Calculate discount details without creating an offer.
    Useful for previewing the discount before creating the offer.
    """
    if discount_percentage <= 0 or discount_percentage >= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount percentage must be between 0 and 100"
        )
    
    discount_details = crud_offer.calculate_discount_details(db, plan_id, discount_percentage)
    if not discount_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found or invalid discount percentage"
        )
    
    return DiscountCalculationResponse(**discount_details)

# GET ALL OFFERS
@offer_router.get("/", response_model=List[OfferResponse])
async def get_offers(
    plan_id: Optional[int] = Query(None, description="Filter by plan"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive/expired)"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all offers with optional filtering by plan and status.
    """
    offers = crud_offer.get_all(db, plan_id=plan_id, status=status, skip=skip, limit=limit)
    
    # Add status to each offer and format dates
    response_offers = []
    for offer in offers:
        offer_status = crud_offer.calculate_offer_status(offer)
        response_data = {
            "offer_id": offer.offer_id,
            "plan_id": offer.plan_id,
            "offer_name": offer.offer_name,
            "description": offer.description,
            "discounted_price": float(offer.discounted_price),
            "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
            "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
            "status": offer_status,
            "created_at": offer.created_at
        }
        response_offers.append(OfferResponse(**response_data))
    
    return response_offers

# GET ACTIVE OFFERS
@offer_router.get("/active", response_model=List[OfferResponse])
async def get_active_offers(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all currently active offers (valid_from <= current_time <= valid_until).
    """
    offers = crud_offer.get_active_offers(db)
    
    # Format dates for response
    response_offers = []
    for offer in offers:
        response_data = {
            "offer_id": offer.offer_id,
            "plan_id": offer.plan_id,
            "offer_name": offer.offer_name,
            "description": offer.description,
            "discounted_price": float(offer.discounted_price),
            "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
            "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
            "status": OfferStatus.active,
            "created_at": offer.created_at
        }
        response_offers.append(OfferResponse(**response_data))
    
    return response_offers

# GET OFFER BY ID
@offer_router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific offer by ID.
    """
    offer = crud_offer.get(db, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Calculate and add status to response
    offer_status = crud_offer.calculate_offer_status(offer)
    response_data = {
        "offer_id": offer.offer_id,
        "plan_id": offer.plan_id,
        "offer_name": offer.offer_name,
        "description": offer.description,
        "discounted_price": float(offer.discounted_price),
        "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
        "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
        "status": offer_status,
        "created_at": offer.created_at
    }
    
    return OfferResponse(**response_data)

# GET OFFERS BY PLAN
@offer_router.get("/plan/{plan_id}", response_model=List[OfferResponse])
async def get_offers_by_plan(
    plan_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all offers for a specific plan.
    """
    # Check if plan exists
    plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    offers = crud_offer.get_by_plan(db, plan_id)
    
    # Add status to each offer and format dates
    response_offers = []
    for offer in offers:
        offer_status = crud_offer.calculate_offer_status(offer)
        response_data = {
            "offer_id": offer.offer_id,
            "plan_id": offer.plan_id,
            "offer_name": offer.offer_name,
            "description": offer.description,
            "discounted_price": float(offer.discounted_price),
            "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
            "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
            "status": offer_status,
            "created_at": offer.created_at
        }
        response_offers.append(OfferResponse(**response_data))
    
    return response_offers

# UPDATE OFFER
@offer_router.put("/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing offer.
    """
    offer = crud_offer.update(db, offer_id, offer_data)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    
    # Calculate and add status to response
    offer_status = crud_offer.calculate_offer_status(offer)
    response_data = {
        "offer_id": offer.offer_id,
        "plan_id": offer.plan_id,
        "offer_name": offer.offer_name,
        "description": offer.description,
        "discounted_price": float(offer.discounted_price),
        "valid_from": offer.valid_from.strftime('%d.%m.%Y %H:%M'),
        "valid_until": offer.valid_until.strftime('%d.%m.%Y %H:%M'),
        "status": offer_status,
        "created_at": offer.created_at
    }
    
    return OfferResponse(**response_data)

# DELETE OFFER
@offer_router.delete("/{offer_id}")
async def delete_offer(
    offer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an offer.
    """
    offer = crud_offer.delete(db, offer_id)
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offer not found"
        )
    return {"message": "Offer deleted successfully"}


# ==========================================================
# 💳 TRANSACTION MONITORING ROUTES
# ==========================================================
transaction_router = APIRouter(prefix="/transactions", tags=["Transaction Monitoring"])

@transaction_router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    customer_phone: Optional[str] = Query(None, description="Filter by customer phone"),
    plan_id: Optional[int] = Query(None, description="Filter by plan"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all transactions with filtering options.
    """
    filter_params = TransactionFilter(
        customer_id=customer_id,
        customer_phone=customer_phone,
        plan_id=plan_id,
        transaction_type=transaction_type,
        payment_status=payment_status,
        payment_method=payment_method,
        date_from=date_from,
        date_to=date_to
    )
    
    transactions_with_details = crud_transaction.get_all_with_details(
        db, filter=filter_params, skip=skip, limit=limit
    )
    
    response_transactions = []
    for transaction, cust_name, cust_phone, plan_name, offer_name in transactions_with_details:
        response_data = {
            "transaction_id": transaction.transaction_id,
            "customer_id": transaction.customer_id,
            "plan_id": transaction.plan_id,
            "offer_id": transaction.offer_id,
            "recipient_phone_number": transaction.recipient_phone_number,
            "transaction_type": transaction.transaction_type,
            "original_amount": float(transaction.original_amount),
            "discount_amount": float(transaction.discount_amount),
            "discount_type": transaction.discount_type,
            "final_amount": float(transaction.final_amount),
            "payment_method": transaction.payment_method,
            "payment_status": transaction.payment_status,
            "transaction_date": transaction.transaction_date,
            "customer_name": cust_name,
            "customer_phone": cust_phone,
            "plan_name": plan_name,
            "offer_name": offer_name
        }
        response_transactions.append(TransactionResponse(**response_data))
    
    return response_transactions

@transaction_router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific transaction.
    """
    transaction_data = crud_transaction.get_with_details(db, transaction_id)
    if not transaction_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    transaction, cust_name, cust_phone, plan_name, offer_name = transaction_data
    
    response_data = {
        "transaction_id": transaction.transaction_id,
        "customer_id": transaction.customer_id,
        "plan_id": transaction.plan_id,
        "offer_id": transaction.offer_id,
        "recipient_phone_number": transaction.recipient_phone_number,
        "transaction_type": transaction.transaction_type,
        "original_amount": float(transaction.original_amount),
        "discount_amount": float(transaction.discount_amount),
        "discount_type": transaction.discount_type,
        "final_amount": float(transaction.final_amount),
        "payment_method": transaction.payment_method,
        "payment_status": transaction.payment_status,
        "transaction_date": transaction.transaction_date,
        "customer_name": cust_name,
        "customer_phone": cust_phone,
        "plan_name": plan_name,
        "offer_name": offer_name
    }
    
    return TransactionResponse(**response_data)

@transaction_router.post("/export")
async def export_transactions(
    export_request: TransactionExportRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Export transactions in CSV or JSON format.
    """
    transactions_with_details = crud_transaction.get_all_with_details(
        db, filter=export_request, skip=0, limit=10000  # Increased limit for export
    )
    
    if export_request.export_format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Transaction ID", "Customer", "Customer Phone", "Plan", "Offer",
            "Transaction Type", "Original Amount", "Discount", "Final Amount",
            "Payment Method", "Payment Status", "Transaction Date"
        ])
        
        # Write data
        for transaction, cust_name, cust_phone, plan_name, offer_name in transactions_with_details:
            writer.writerow([
                transaction.transaction_id,
                cust_name or "",
                cust_phone or "",
                plan_name or "",
                offer_name or "",
                transaction.transaction_type.value,
                float(transaction.original_amount),
                float(transaction.discount_amount),
                float(transaction.final_amount),
                transaction.payment_method.value,
                transaction.payment_status.value,
                transaction.transaction_date.isoformat()
            ])
        
        content = output.getvalue()
        output.close()
        
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
        )
    
    elif export_request.export_format.lower() == "json":
        transactions_list = []
        for transaction, cust_name, cust_phone, plan_name, offer_name in transactions_with_details:
            transactions_list.append({
                "transaction_id": transaction.transaction_id,
                "customer_name": cust_name,
                "customer_phone": cust_phone,
                "plan_name": plan_name,
                "offer_name": offer_name,
                "transaction_type": transaction.transaction_type.value,
                "original_amount": float(transaction.original_amount),
                "discount_amount": float(transaction.discount_amount),
                "final_amount": float(transaction.final_amount),
                "payment_method": transaction.payment_method.value,
                "payment_status": transaction.payment_status.value,
                "transaction_date": transaction.transaction_date.isoformat()
            })
        
        content = json.dumps(transactions_list, indent=2)
        
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=transactions_export.json"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format. Use 'csv' or 'json'."
        )

# ==========================================================
# 📱 SUBSCRIPTION MANAGEMENT ROUTES
# ==========================================================
subscription_router = APIRouter(prefix="/subscriptions", tags=["Subscription Management"])

@subscription_router.get("/active")
async def get_active_subscriptions(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all active subscriptions (only currently active ones).
    """
    current_time = datetime.utcnow()
    
    query = db.query(Subscription).filter(
        Subscription.activation_date.isnot(None),  # Must be activated
        Subscription.activation_date <= current_time,  # Activation date has passed
        Subscription.expiry_date > current_time  # Not expired yet
    )
    
    if customer_id:
        query = query.filter(Subscription.customer_id == customer_id)
    
    subscriptions = query.all()
    
    # Enhance with customer and plan details
    enhanced_subscriptions = []
    for subscription in subscriptions:
        customer = db.query(Customer).filter(Customer.customer_id == subscription.customer_id).first()
        plan = db.query(Plan).filter(Plan.plan_id == subscription.plan_id).first()
        
        enhanced_subscriptions.append({
            "subscription_id": subscription.subscription_id,
            "customer_id": subscription.customer_id,
            "customer_name": customer.full_name if customer else "Unknown",
            "customer_phone": customer.phone_number if customer else "Unknown",
            "plan_id": subscription.plan_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "phone_number": subscription.phone_number,
            "is_topup": subscription.is_topup,
            "activation_date": subscription.activation_date,
            "expiry_date": subscription.expiry_date,
            "data_balance_gb": float(subscription.data_balance_gb) if subscription.data_balance_gb else None,
            "daily_data_limit_gb": float(subscription.daily_data_limit_gb) if subscription.daily_data_limit_gb else None,
            "daily_data_used_gb": float(subscription.daily_data_used_gb) if subscription.daily_data_used_gb else None
        })
    
    return enhanced_subscriptions

@subscription_router.get("/queue")
async def get_activation_queue(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get the subscription activation queue.
    """
    # Only get unprocessed queue items
    query = db.query(SubscriptionActivationQueue).filter(
        SubscriptionActivationQueue.processed_at.is_(None)  # Only unprocessed items
    )
    
    if customer_id:
        query = query.filter(SubscriptionActivationQueue.customer_id == customer_id)
    
    queue_items = query.order_by(SubscriptionActivationQueue.queue_position).all()
    
    enhanced_queue = []
    for item in queue_items:
        customer = db.query(Customer).filter(Customer.customer_id == item.customer_id).first()
        plan = db.query(Plan).filter(Plan.plan_id == item.subscription.plan_id).first()
        
        enhanced_queue.append({
            "queue_id": item.queue_id,
            "subscription_id": item.subscription_id,
            "customer_id": item.customer_id,
            "customer_name": customer.full_name if customer else "Unknown",
            "customer_phone": customer.phone_number if customer else "Unknown",
            "plan_id": item.subscription.plan_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "phone_number": item.phone_number,
            "queue_position": item.queue_position,
            "expected_activation_date": item.expected_activation_date,
            "expected_expiry_date": item.expected_expiry_date,
            "created_at": item.created_at
        })
    
    return enhanced_queue


# ==========================================================
# 👥 CUSTOMER MANAGEMENT ROUTES
# ==========================================================
customer_router = APIRouter(prefix="/customers", tags=["Customer Management"])

@customer_router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    phone_number: Optional[str] = Query(None, description="Filter by phone number"),
    full_name: Optional[str] = Query(None, description="Filter by full name"),
    account_status: Optional[AccountStatus] = Query(None, description="Filter by account status"),
    days_inactive_min: Optional[int] = Query(None, description="Minimum days inactive"),
    days_inactive_max: Optional[int] = Query(None, description="Maximum days inactive"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all customers with filtering options.
    """
    filter_params = CustomerFilter(
        phone_number=phone_number,
        full_name=full_name,
        account_status=account_status,
        days_inactive_min=days_inactive_min,
        days_inactive_max=days_inactive_max
    )
    
    customers = crud_customer.get_all(db, filter=filter_params, skip=skip, limit=limit)
    return customers

@customer_router.get("/search")
async def search_customers(
    search_term: str = Query(..., description="Search by phone number or name"),
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(50, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Search customers by phone number or name.
    """
    customers = crud_customer.search_customers(db, search_term=search_term, skip=skip, limit=limit)
    return customers

@customer_router.get("/stats", response_model=CustomerStatsResponse)
async def get_customer_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get customer statistics.
    """
    stats = crud_customer.get_customer_stats(db)
    return CustomerStatsResponse(**stats)

@customer_router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer_details(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific customer.
    """
    customer_data = crud_customer.get_customer_details(db, customer_id)
    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer = customer_data['customer']
    
    response_data = {
        "customer_id": customer.customer_id,
        "phone_number": customer.phone_number,
        "full_name": customer.full_name,
        "account_status": customer.account_status,
        "profile_picture_url": customer.profile_picture_url,
        "last_active_plan_date": customer.last_active_plan_date,
        "days_inactive": customer.days_inactive,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
        "total_transactions": customer_data['total_transactions'],
        "total_spent": customer_data['total_spent'],
        "active_subscriptions": customer_data['active_subscriptions'],
        "queued_subscriptions": customer_data['queued_subscriptions'],
        "referral_code": customer_data['referral_code']
    }
    
    return CustomerDetailResponse(**response_data)

@customer_router.get("/{customer_id}/transactions")
async def get_customer_transactions(
    customer_id: int,
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get transaction history for a customer.
    """
    # Verify customer exists
    customer = crud_customer.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    transactions = crud_customer.get_customer_transactions(db, customer_id, skip=skip, limit=limit)
    
    # Enhance with plan and offer details
    enhanced_transactions = []
    for transaction in transactions:
        plan = db.query(Plan).filter(Plan.plan_id == transaction.plan_id).first()
        offer = db.query(Offer).filter(Offer.offer_id == transaction.offer_id).first() if transaction.offer_id else None
        
        enhanced_transactions.append({
            "transaction_id": transaction.transaction_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "offer_name": offer.offer_name if offer else None,
            "recipient_phone_number": transaction.recipient_phone_number,
            "transaction_type": transaction.transaction_type.value,
            "original_amount": float(transaction.original_amount),
            "discount_amount": float(transaction.discount_amount),
            "final_amount": float(transaction.final_amount),
            "payment_method": transaction.payment_method.value,
            "payment_status": transaction.payment_status.value,
            "transaction_date": transaction.transaction_date
        })
    
    return enhanced_transactions

@customer_router.get("/{customer_id}/subscriptions")
async def get_customer_subscriptions(
    customer_id: int,
    skip: int = Query(0, description="Skip records"),
    limit: int = Query(100, description="Limit records"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get subscription history for a customer.
    """
    # Verify customer exists
    customer = crud_customer.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    subscriptions = crud_customer.get_customer_subscriptions(db, customer_id, skip=skip, limit=limit)
    
    # Enhance with plan details
    enhanced_subscriptions = []
    for subscription in subscriptions:
        plan = db.query(Plan).filter(Plan.plan_id == subscription.plan_id).first()
        
        enhanced_subscriptions.append({
            "subscription_id": subscription.subscription_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "phone_number": subscription.phone_number,
            "is_topup": subscription.is_topup,
            "activation_date": subscription.activation_date,
            "expiry_date": subscription.expiry_date,
            "data_balance_gb": float(subscription.data_balance_gb) if subscription.data_balance_gb else None,
            "daily_data_limit_gb": float(subscription.daily_data_limit_gb) if subscription.daily_data_limit_gb else None,
            "daily_data_used_gb": float(subscription.daily_data_used_gb) if subscription.daily_data_used_gb else None,
            "status": "active" if subscription.expiry_date > datetime.utcnow() else "expired",
            "created_at": subscription.created_at
        })
    
    return enhanced_subscriptions

@customer_router.get("/{customer_id}/queue")
async def get_customer_queued_subscriptions(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get queued subscriptions for a customer.
    """
    # Verify customer exists
    customer = crud_customer.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    queue_items = crud_customer.get_customer_queued_subscriptions(db, customer_id)
    
    enhanced_queue = []
    for item in queue_items:
        plan = db.query(Plan).filter(Plan.plan_id == item.subscription.plan_id).first()
        
        enhanced_queue.append({
            "queue_id": item.queue_id,
            "subscription_id": item.subscription_id,
            "plan_name": plan.plan_name if plan else "Unknown",
            "phone_number": item.phone_number,
            "queue_position": item.queue_position,
            "expected_activation_date": item.expected_activation_date,
            "expected_expiry_date": item.expected_expiry_date,
            "created_at": item.created_at
        })
    
    return enhanced_queue

@customer_router.post("/{customer_id}/deactivate")
async def deactivate_customer(
    customer_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate a customer account.
    """
    customer = crud_customer.deactivate_account(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {"message": "Customer account deactivated successfully", "customer_id": customer_id}

# ==========================================================
# 📊 DASHBOARD ANALYTICS ROUTES
# ==========================================================
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])

@dashboard_router.get("/")
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.account_status == "active").count()
    total_transactions = db.query(Transaction).count()

    today = datetime.utcnow().date()
    todays_transactions = db.query(Transaction).filter(
        func.date(Transaction.transaction_date) == today
    ).count()

    total_revenue_result = db.query(func.sum(Transaction.final_amount)).filter(
        Transaction.payment_status == "success"
    ).first()
    total_revenue = float(total_revenue_result[0]) if total_revenue_result[0] else 0.0

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_transactions": total_transactions,
        "todays_transactions": todays_transactions,
        "total_revenue": total_revenue
    }