from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil

from app.database import get_db
from app.models.models import Admin
from app.core.auth import get_current_admin
from app.schemas.backup_restore import *
from app.crud.crud_backup_restore import crud_backup_restore
from app.services.backup_service import backup_service
from app.services.backup_scheduler import backup_scheduler

router = APIRouter(prefix="/backup-restore", tags=["Admin - Backup & Restore"])

@router.post("/backup/manual", response_model=BackupResponse)
async def create_manual_backup(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a manual backup of essential system data.
    """
    result = backup_service.perform_backup(db, current_admin.admin_id, "manual")
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['error']
        )
    
    backup = crud_backup_restore.get_backup(db, result['backup_id'])
    
    # Create response with all required fields
    response_data = {
        "backup_id": backup.backup_id,
        "admin_id": backup.admin_id,
        "file_name": backup.file_name,
        "path": backup.path,
        "type": backup.type,
        "data_list": backup.data_list,
        "date": backup.date,
        "message": f"Backup created successfully with {result['data_size']} bytes of data"
    }
    
    return BackupResponse(**response_data)

@router.get("/backup", response_model=List[BackupResponse])
async def get_backup_history(
    skip: int = 0,
    limit: int = 100,
    backup_type: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get backup history with filtering options.
    """
    backups = crud_backup_restore.get_all_backups(db, skip=skip, limit=limit, backup_type=backup_type)
    return backups


@router.post("/backup/schedule", response_model=ScheduleResponse)
async def set_backup_schedule(
    schedule_data: ScheduleRequest,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Set automated backup schedule (daily, weekly, monthly).
    """
    result = backup_scheduler.set_schedule(schedule_data.frequency, schedule_data.time_of_day)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    # Start scheduler if not already running
    if not backup_scheduler.is_running:
        background_tasks.add_task(backup_scheduler.start)
    
    return ScheduleResponse(**result)

@router.get("/backup/schedule/status", response_model=ScheduleStatusResponse)
async def get_schedule_status(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get current backup schedule status.
    """
    status = backup_scheduler.get_schedule_status()
    return ScheduleStatusResponse(**status)

@router.get("/backup/schedule/options", response_model=ScheduleOptionsResponse)
async def get_schedule_options(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get available backup schedule options.
    """
    options = backup_service.get_backup_schedule_options()
    return ScheduleOptionsResponse(options=options)

@router.post("/restore/{backup_id}", response_model=RestoreResponse)
async def restore_from_backup(
    backup_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Restore system data from a specific backup.
    WARNING: This will overwrite existing data.
    """
    # First, verify the backup exists
    backup = crud_backup_restore.get_backup(db, backup_id)
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found"
        )
    
    result = backup_service.perform_restore(db, current_admin.admin_id, backup_id)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['error']
        )
    
    # Create restore record 
    restore = crud_backup_restore.create_restore(
        db, 
        current_admin.admin_id, 
        backup_id,  
        backup.file_name,  
        {  
            'tables_to_restore': result.get('tables_to_restore', []),
            'record_counts': result.get('record_counts', {}),
            'backup_source_id': backup_id
        }
    )
    
    # Create response with all required fields
    response_data = {
        "restore_id": restore.restore_id,
        "admin_id": restore.admin_id,
        "file_name": restore.file_name,
        "path": restore.path,
        "type": restore.type,
        "data_list": restore.data_list,
        "date": restore.date,
        "message": "Restore process initiated successfully (simulation mode)"
    }
    
    return RestoreResponse(**response_data)

@router.get("/restore", response_model=List[RestoreResponse])
async def get_restore_history(
    skip: int = 0,
    limit: int = 100,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get restore operation history.
    """
    restores = crud_backup_restore.get_all_restores(db, skip=skip, limit=limit)
    return restores

@router.get("/stats", response_model=BackupStatsResponse)
async def get_backup_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get backup and restore statistics.
    """
    stats = crud_backup_restore.get_backup_stats(db)
    return BackupStatsResponse(**stats)

@router.delete("/backup/{backup_id}")
async def delete_backup(
    backup_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a specific backup (both record and file).
    """
    backup = crud_backup_restore.get_backup(db, backup_id)
    if not backup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found"
        )
    
    try:
        # Delete backup file
        file_path = os.path.join("backups", backup.file_name)
        zip_path = file_path.replace('.json', '.zip')
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Delete database record
        db.delete(backup)
        db.commit()
        
        return {"message": "Backup deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting backup: {str(e)}"
        )