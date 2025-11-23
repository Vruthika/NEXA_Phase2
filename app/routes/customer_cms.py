from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.core.auth import get_current_customer
from app.models.models import Customer
from app.schemas.cms import HeaderResponse, CarouselResponse, FAQResponse, CMSListResponse
from app.mongo import get_mongo_db
from app.utils.mongo_utils import bson_to_json

router = APIRouter(prefix="/customer/cms", tags=["Customer - CMS Content"])

@router.get("/content", response_model=CMSListResponse)
async def get_cms_content(
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get all CMS content for customer frontend
    """
    # Get headers
    headers_collection = db.headers
    headers = []
    async for header in headers_collection.find().sort("created_at", -1):
        header_data = bson_to_json(header)
        header_data["id"] = str(header["_id"])
        headers.append(HeaderResponse(**header_data))
    
    # Get carousels
    carousels_collection = db.carousels
    carousels = []
    async for carousel in carousels_collection.find().sort("order", 1):
        carousel_data = bson_to_json(carousel)
        carousel_data["id"] = str(carousel["_id"])
        carousels.append(CarouselResponse(**carousel_data))
    
    # Get FAQs
    faqs_collection = db.faqs
    faqs = []
    async for faq in faqs_collection.find().sort("order", 1):
        faq_data = bson_to_json(faq)
        faq_data["id"] = str(faq["_id"])
        faqs.append(FAQResponse(**faq_data))
    
    return CMSListResponse(
        headers=headers,
        carousels=carousels,
        faqs=faqs
    )

@router.get("/headers", response_model=List[HeaderResponse])
async def get_customer_headers(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get headers for customer (public endpoint)
    """
    headers_collection = db.headers
    headers = []
    
    async for header in headers_collection.find().sort("created_at", -1):
        header_data = bson_to_json(header)
        header_data["id"] = str(header["_id"])
        headers.append(HeaderResponse(**header_data))
    
    return headers

@router.get("/carousels", response_model=List[CarouselResponse])
async def get_customer_carousels(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get carousel items for customer (public endpoint)
    """
    carousels_collection = db.carousels
    carousels = []
    
    async for carousel in carousels_collection.find().sort("order", 1):
        carousel_data = bson_to_json(carousel)
        carousel_data["id"] = str(carousel["_id"])
        carousels.append(CarouselResponse(**carousel_data))
    
    return carousels

@router.get("/faqs", response_model=List[FAQResponse])
async def get_customer_faqs(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get FAQ items for customer (public endpoint)
    """
    faqs_collection = db.faqs
    faqs = []
    
    async for faq in faqs_collection.find().sort("order", 1):
        faq_data = bson_to_json(faq)
        faq_data["id"] = str(faq["_id"])
        faqs.append(FAQResponse(**faq_data))
    
    return faqs