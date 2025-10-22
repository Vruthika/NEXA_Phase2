from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.postpaid_data_addon import PostpaidDataAddon
from datetime import datetime

class PostpaidDataAddonCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, addon_id: int) -> PostpaidDataAddon:
        return self.db.query(PostpaidDataAddon).filter(PostpaidDataAddon.addon_id == addon_id).first()
    
    def get_by_activation_id(self, activation_id: int):
        return self.db.query(PostpaidDataAddon).filter(PostpaidDataAddon.activation_id == activation_id).all()
    
    def get_active_addons(self, activation_id: int):
        return self.db.query(PostpaidDataAddon).filter(
            and_(
                PostpaidDataAddon.activation_id == activation_id,
                PostpaidDataAddon.status == 'active'
            )
        ).all()
    
    def create(self, addon_data: dict) -> PostpaidDataAddon:
        addon = PostpaidDataAddon(**addon_data)
        self.db.add(addon)
        self.db.commit()
        self.db.refresh(addon)
        return addon
    
    def update(self, addon_id: int, addon_data: dict) -> PostpaidDataAddon:
        addon = self.get_by_id(addon_id)
        if addon:
            for key, value in addon_data.items():
                setattr(addon, key, value)
            self.db.commit()
            self.db.refresh(addon)
        return addon
    
    def update_status(self, addon_id: int, status: str) -> PostpaidDataAddon:
        addon = self.get_by_id(addon_id)
        if addon:
            addon.status = status
            self.db.commit()
            self.db.refresh(addon)
        return addon
    
    def expire_addons(self, activation_id: int):
        addons = self.db.query(PostpaidDataAddon).filter(
            and_(
                PostpaidDataAddon.activation_id == activation_id,
                PostpaidDataAddon.valid_until <= datetime.utcnow(),
                PostpaidDataAddon.status == 'active'
            )
        ).all()
        
        for addon in addons:
            addon.status = 'expired'
        
        self.db.commit()
        return addons