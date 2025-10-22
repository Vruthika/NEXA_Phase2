from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_admin
from app.services.backup_restore_service import BackupRestoreService

router = APIRouter()

@router.post("/backup")
async def create_backup(
    backup_type: str = "manual",
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    backup_service = BackupRestoreService(db)
    backup = backup_service.create_backup(current_admin.admin_id, backup_type)
    
    return {
        "message": "Backup created successfully",
        "backup_id": backup.backup_id,
        "file_name": backup.file_name
    }

@router.get("/backups")
async def get_backups(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    backup_service = BackupRestoreService(db)
    return backup_service.get_backups()

@router.post("/restore/{backup_id}")
async def restore_backup(
    backup_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    backup_service = BackupRestoreService(db)
    restore = backup_service.restore_backup(backup_id, current_admin.admin_id)
    
    return {
        "message": "Restore completed successfully",
        "restore_id": restore.restore_id
    }

@router.get("/restores")
async def get_restores(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    backup_service = BackupRestoreService(db)
    return backup_service.get_restores()