from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db as get_sql_db
from app.models.models import Category

from app.database import get_db
from app.models.models import Admin
from app.core.auth import get_current_admin
from app.schemas.cms import *
from app.mongo import get_mongo_db
from app.utils.mongo_utils import bson_to_json, create_timestamps, update_timestamp

router = APIRouter(prefix="/cms", tags=["Admin - CMS Management"])

# ============================================
# HEADER MANAGEMENT
# ============================================

@router.post("/headers", response_model=HeaderResponse)
async def create_header(
    header_data: HeaderCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Create a new header banner
    """
    headers_collection = db.headers
    
    # Check if header already exists (we'll allow only one header for now)
    existing_header = await headers_collection.find_one({})
    if existing_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header already exists. Use update to modify existing header."
        )
    
    header_doc = header_data.model_dump()
    header_doc.update(create_timestamps())
    
    result = await headers_collection.insert_one(header_doc)
    
    # Get the created document
    created_header = await headers_collection.find_one({"_id": result.inserted_id})
    if not created_header:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create header"
        )
    
    # Convert to response format
    response_data = bson_to_json(created_header)
    response_data["id"] = str(created_header["_id"])
    
    return HeaderResponse(**response_data)

@router.get("/headers", response_model=List[HeaderResponse])
async def get_headers(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get all headers
    """
    headers_collection = db.headers
    headers = []
    
    async for header in headers_collection.find().sort("created_at", -1):
        header_data = bson_to_json(header)
        header_data["id"] = str(header["_id"])
        headers.append(HeaderResponse(**header_data))
    
    return headers

@router.get("/headers/{header_id}", response_model=HeaderResponse)
async def get_header(
    header_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get a specific header by ID
    """
    from bson import ObjectId
    
    headers_collection = db.headers
    
    try:
        header = await headers_collection.find_one({"_id": ObjectId(header_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid header ID"
        )
    
    if not header:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Header not found"
        )
    
    header_data = bson_to_json(header)
    header_data["id"] = str(header["_id"])
    
    return HeaderResponse(**header_data)

@router.put("/headers/{header_id}", response_model=HeaderResponse)
async def update_header(
    header_id: str,
    header_data: HeaderUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Update a header
    """
    from bson import ObjectId
    
    headers_collection = db.headers
    
    update_data = header_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    update_data.update(update_timestamp())
    
    try:
        updated_header = await headers_collection.find_one_and_update(
            {"_id": ObjectId(header_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid header ID"
        )
    
    if not updated_header:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Header not found"
        )
    
    header_response = bson_to_json(updated_header)
    header_response["id"] = str(updated_header["_id"])
    
    return HeaderResponse(**header_response)

@router.delete("/headers/{header_id}")
async def delete_header(
    header_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Delete a header
    """
    from bson import ObjectId
    
    headers_collection = db.headers
    
    try:
        result = await headers_collection.delete_one({"_id": ObjectId(header_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid header ID"
        )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Header not found"
        )
    
    return {"message": "Header deleted successfully"}

# ============================================
# CAROUSEL MANAGEMENT
# ============================================

@router.post("/carousels", response_model=CarouselResponse)
async def create_carousel(
    carousel_data: CarouselCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Create a new carousel item
    """
    try:
        print(f"Creating carousel with data: {carousel_data}")
        
        carousels_collection = db.carousels
        
        carousel_doc = carousel_data.model_dump()
        print(f"Carousel doc before timestamps: {carousel_doc}")
        
        carousel_doc.update(create_timestamps())
        print(f"Carousel doc after timestamps: {carousel_doc}")
        
        result = await carousels_collection.insert_one(carousel_doc)
        print(f"Insert result: {result.inserted_id}")
        
        created_carousel = await carousels_collection.find_one({"_id": result.inserted_id})
        print(f"Created carousel from DB: {created_carousel}")
        
        if not created_carousel:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create carousel item"
            )
        
        carousel_response = bson_to_json(created_carousel)
        print(f"After bson_to_json: {carousel_response}")
        
        carousel_response["id"] = str(created_carousel["_id"])
        print(f"Final response data: {carousel_response}")
        
        response = CarouselResponse(**carousel_response)
        print(f"Final CarouselResponse: {response}")
        
        return response
        
    except Exception as e:
        print(f"Error in create_carousel: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create carousel: {str(e)}"
        )
             
@router.get("/carousels", response_model=List[CarouselResponse])
async def get_carousels(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get all carousel items ordered by 'order' field
    """
    carousels_collection = db.carousels
    carousels = []
    
    async for carousel in carousels_collection.find().sort("order", 1):
        carousel_data = bson_to_json(carousel)
        carousel_data["id"] = str(carousel["_id"])
        carousels.append(CarouselResponse(**carousel_data))
    
    return carousels

@router.put("/carousels/{carousel_id}", response_model=CarouselResponse)
async def update_carousel(
    carousel_id: str,
    carousel_data: CarouselUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Update a carousel item
    """
    from bson import ObjectId
    
    carousels_collection = db.carousels
    
    update_data = carousel_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    update_data.update(update_timestamp())
    
    try:
        updated_carousel = await carousels_collection.find_one_and_update(
            {"_id": ObjectId(carousel_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid carousel ID"
        )
    
    if not updated_carousel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carousel item not found"
        )
    
    carousel_response = bson_to_json(updated_carousel)
    carousel_response["id"] = str(updated_carousel["_id"])
    
    return CarouselResponse(**carousel_response)
@router.delete("/carousels/{carousel_id}")
async def delete_carousel(
    carousel_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Delete a carousel item
    """
    from bson import ObjectId
    
    carousels_collection = db.carousels
    
    try:
        result = await carousels_collection.delete_one({"_id": ObjectId(carousel_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid carousel ID"
        )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carousel item not found"
        )
    
    return {"message": "Carousel item deleted successfully"}

# ============================================
# FAQ MANAGEMENT
# ============================================

@router.post("/faqs", response_model=FAQResponse)
async def create_faq(
    faq_data: FAQCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Create a new FAQ item
    """
    faqs_collection = db.faqs
    
    faq_doc = faq_data.model_dump()
    faq_doc.update(create_timestamps())
    
    result = await faqs_collection.insert_one(faq_doc)
    
    created_faq = await faqs_collection.find_one({"_id": result.inserted_id})
    if not created_faq:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create FAQ item"
        )
    
    faq_response = bson_to_json(created_faq)
    faq_response["id"] = str(created_faq["_id"])
    
    return FAQResponse(**faq_response)

@router.get("/faqs", response_model=List[FAQResponse])
async def get_faqs(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get all FAQ items ordered by 'order' field
    """
    faqs_collection = db.faqs
    faqs = []
    
    async for faq in faqs_collection.find().sort("order", 1):
        faq_data = bson_to_json(faq)
        faq_data["id"] = str(faq["_id"])
        faqs.append(FAQResponse(**faq_data))
    
    return faqs

@router.put("/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: str,
    faq_data: FAQUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Update a FAQ item
    """
    from bson import ObjectId
    
    faqs_collection = db.faqs
    
    update_data = faq_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    update_data.update(update_timestamp())
    
    try:
        updated_faq = await faqs_collection.find_one_and_update(
            {"_id": ObjectId(faq_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid FAQ ID"
        )
    
    if not updated_faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ item not found"
        )
    
    faq_response = bson_to_json(updated_faq)
    faq_response["id"] = str(updated_faq["_id"])
    
    return FAQResponse(**faq_response)

@router.delete("/faqs/{faq_id}")
async def delete_faq(
    faq_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Delete a FAQ item
    """
    from bson import ObjectId
    
    faqs_collection = db.faqs
    
    try:
        result = await faqs_collection.delete_one({"_id": ObjectId(faq_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid FAQ ID"
        )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ item not found"
        )
    
    return {"message": "FAQ item deleted successfully"}

# ============================================
# CMS OVERVIEW & REORDERING
# ============================================

@router.get("/overview", response_model=CMSListResponse)
async def get_cms_overview(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get complete CMS data overview
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

@router.post("/reorder")
async def reorder_items(
    reorder_data: CMSReorderRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Reorder items in carousel or FAQ collections
    """
    from bson import ObjectId
    
    collection_map = {
        "carousel": db.carousels,
        "faq": db.faqs
    }
    
    if reorder_data.collection_type not in collection_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection type. Use 'carousel' or 'faq'"
        )
    
    collection = collection_map[reorder_data.collection_type]
    
    try:
        # Update the order of the specified item
        result = await collection.update_one(
            {"_id": ObjectId(reorder_data.item_id)},
            {"$set": {"order": reorder_data.new_order, "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or order unchanged"
        )
    
    return {"message": f"{reorder_data.collection_type.title()} item reordered successfully"}