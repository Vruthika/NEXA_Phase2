# app/schemas/__init__.py
# Add the new customer operations schemas
from .customer_operations import (
    CustomerProfileResponse,
    CustomerProfileUpdate,
    CustomerTransactionResponse,
    CustomerSubscriptionResponse,
    CustomerQueueResponse,
    PlanResponseForCustomer,
    OfferResponseForCustomer,
    RechargeRequest,
    RechargeResponse
)

# Add to __all__ list
__all__ = [
    # ... existing imports
    "CustomerProfileResponse",
    "CustomerProfileUpdate", 
    "CustomerTransactionResponse",
    "CustomerSubscriptionResponse",
    "CustomerQueueResponse",
    "PlanResponseForCustomer",
    "OfferResponseForCustomer",
    "RechargeRequest",
    "RechargeResponse"
]