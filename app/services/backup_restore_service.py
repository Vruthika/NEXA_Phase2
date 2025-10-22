from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json
from datetime import datetime
from app.crud.backup_crud import BackupCRUD
from app.crud.restore_crud import RestoreCRUD

class BackupRestoreService:
    def __init__(self, db: Session):
        self.db = db
        self.backup_crud = BackupCRUD(db)
        self.restore_crud = RestoreCRUD(db)
    
    def create_backup(self, admin_id: int, backup_type: str = "manual"):
        # In a real implementation, this would backup the actual database
        # For demo purposes, we'll create a metadata backup
        
        backup_data = {
            "tables": [
                "customers", "plans", "transactions", "subscriptions",
                "postpaid_activations", "referral_program"
            ],
            "backup_timestamp": datetime.utcnow().isoformat(),
            "record_count": "simulated"
        }
        
        file_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = f"/backups/{file_name}"
        
        backup_dict = {
            "admin_id": admin_id,
            "file_name": file_name,
            "path": path,
            "type": backup_type,
            "data_list": backup_data
        }
        
        return self.backup_crud.create(backup_dict)
    
    def get_backups(self):
        return self.backup_crud.get_all()
    
    def restore_backup(self, backup_id: int, admin_id: int):
        backup = self.backup_crud.get_by_id(backup_id)
        if not backup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backup not found"
            )
        
        # In a real implementation, this would restore the actual database
        # For demo purposes, we'll create a restore record
        
        restore_dict = {
            "admin_id": admin_id,
            "file_name": backup.file_name,
            "path": backup.path,
            "type": "manual",
            "data_list": backup.data_list
        }
        
        return self.restore_crud.create(restore_dict)
    
    def get_restores(self):
        return self.restore_crud.get_all()