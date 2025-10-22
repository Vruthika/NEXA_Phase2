from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.postpaid_activation import (
    PostpaidActivationCreate, PostpaidActivationResponse,
    PostpaidSecondaryNumberCreate, PostpaidDataAddonCreate
)
from app.services.postpaid_activation_service import PostpaidActivationService

router = APIRouter()

@router.post("/", response_model=PostpaidActivationResponse, status_code=status.HTTP_201_CREATED)
async def create_postpaid_activation(
    activation_data: PostpaidActivationCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    return postpaid_service.create_activation(current_customer.customer_id, activation_data)

@router.get("/my-activations", response_model=List[PostpaidActivationResponse])
async def get_my_activations(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    return postpaid_service.get_customer_activations(current_customer.customer_id)

@router.get("/{activation_id}", response_model=PostpaidActivationResponse)
async def get_activation_by_id(
    activation_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    activation = postpaid_service.get_activation_by_id(activation_id)
    
    # Verify activation belongs to current customer
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this activation"
        )
    
    return activation

@router.post("/{activation_id}/secondary-numbers", response_model=dict)
async def add_secondary_number(
    activation_id: int,
    secondary_data: PostpaidSecondaryNumberCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    activation = postpaid_service.get_activation_by_id(activation_id)
    
    # Verify activation belongs to current customer
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this activation"
        )
    
    secondary_number = postpaid_service.add_secondary_number(activation_id, secondary_data)
    
    return {
        "message": "Secondary number added successfully",
        "secondary_id": secondary_number.secondary_id,
        "phone_number": secondary_number.phone_number
    }

@router.post("/{activation_id}/data-addons", response_model=dict)
async def add_data_addon(
    activation_id: int,
    addon_data: PostpaidDataAddonCreate,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    activation = postpaid_service.get_activation_by_id(activation_id)
    
    # Verify activation belongs to current customer
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this activation"
        )
    
    addon = postpaid_service.add_data_addon(activation_id, addon_data)
    
    return {
        "message": "Data addon added successfully",
        "addon_id": addon.addon_id,
        "addon_name": addon.addon_name,
        "data_amount_gb": float(addon.data_amount_gb),
        "price": float(addon.addon_price)
    }

@router.post("/{activation_id}/update-usage")
async def update_data_usage(
    activation_id: int,
    data_used_gb: float,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    postpaid_service = PostpaidActivationService(db)
    activation = postpaid_service.get_activation_by_id(activation_id)
    
    # Verify activation belongs to current customer
    if activation.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this activation"
        )
    
    updated_activation = postpaid_service.update_data_usage(activation_id, data_used_gb)
    
    return {
        "message": "Data usage updated successfully",
        "activation_id": activation_id,
        "data_used_gb": data_used_gb,
        "remaining_balance_gb": float(updated_activation.current_data_balance_gb),
        "total_used_gb": float(updated_activation.data_used_gb)
    }