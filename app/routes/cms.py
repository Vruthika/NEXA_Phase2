from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_admin
from app.services.cms_service import CMSService

router = APIRouter()

@router.get("/header")
async def get_header_content(db: Session = Depends(get_db)):
    cms_service = CMSService(db)
    return cms_service.get_header_content()

@router.post("/header")
async def update_header_content(
    content_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    cms_service = CMSService(db)
    return cms_service.update_header_content(content_data)

@router.get("/carousel")
async def get_carousel_items(db: Session = Depends(get_db)):
    cms_service = CMSService(db)
    return cms_service.get_carousel_items()

@router.post("/carousel")
async def update_carousel_item(
    item_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    cms_service = CMSService(db)
    return cms_service.update_carousel_item(item_data)

@router.get("/faqs")
async def get_faqs(db: Session = Depends(get_db)):
    cms_service = CMSService(db)
    return cms_service.get_faqs()

@router.post("/faqs")
async def update_faq(
    faq_data: dict,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    cms_service = CMSService(db)
    return cms_service.update_faq(faq_data)