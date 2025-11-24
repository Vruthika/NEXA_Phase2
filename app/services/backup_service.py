import os
import json
import zipfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.crud.crud_backup_restore import crud_backup_restore
from app.config import settings

class BackupService:
    def __init__(self):
        self.backup_dir = "backups"
        self.max_backups = getattr(settings, 'MAX_BACKUPS', 50) 
        
    def perform_backup(self, db: Session, admin_id: int, backup_type: str = "manual") -> Dict[str, Any]:
        """Perform a complete system backup"""
        try:
            essential_data = crud_backup_restore.get_essential_data(db)
            
            # Create backup record
            backup = crud_backup_restore.create_backup(db, admin_id, backup_type, {
                'tables_backed_up': list(essential_data.keys()),
                'record_counts': {
                    table: len(data) for table, data in essential_data.items() 
                    if table != 'metadata'
                }
            })
            
            # Save backup file
            file_path = os.path.join(self.backup_dir, backup.file_name)
            success = crud_backup_restore.save_backup_file(essential_data, file_path)
            
            if not success:
                # Delete the backup record if file save failed
                db.delete(backup)
                db.commit()
                return {'success': False, 'error': 'Failed to save backup file'}
            
            # Clean up old backups if exceeding limit
            self._cleanup_old_backups(db)
            
            return {
                'success': True,
                'backup_id': backup.backup_id,
                'file_name': backup.file_name,
                'data_size': len(json.dumps(essential_data)),
                'tables_backed_up': list(essential_data.keys()),
                'record_counts': essential_data['metadata']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def perform_restore(self, db: Session, admin_id: int, backup_id: int) -> Dict[str, Any]:
        """Restore system from backup"""
        try:
            # Get backup record
            backup = crud_backup_restore.get_backup(db, backup_id)
            if not backup:
                return {'success': False, 'error': 'Backup not found'}
            
            # Load backup data
            file_path = os.path.join(self.backup_dir, backup.file_name)
            backup_data = crud_backup_restore.load_backup_file(file_path)
            
            if not backup_data:
                return {'success': False, 'error': 'Failed to load backup file'}
            
            # Validate backup data
            if 'metadata' not in backup_data:
                return {'success': False, 'error': 'Invalid backup file format'}
            
            # Create restore record with correct parameters
            restore = crud_backup_restore.create_restore(
                db, 
                admin_id, 
                backup_id, 
                backup.file_name, 
                {  
                    'tables_to_restore': list(backup_data.keys()),
                    'record_counts': backup_data['metadata']
                }
            )
            
            return {
                'success': True,
                'restore_id': restore.restore_id,
                'backup_id': backup_id,
                'tables_to_restore': list(backup_data.keys()),
                'record_counts': backup_data['metadata'],
                'warning': 'This is a simulation. Actual database restoration should be implemented with caution.'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def _cleanup_old_backups(self, db: Session):
        """Remove old backups beyond the maximum limit"""
        try:
            all_backups = crud_backup_restore.get_all_backups(db, limit=1000) 
            
            if len(all_backups) > self.max_backups:
                # Keep the most recent backups, delete the oldest ones
                backups_to_delete = all_backups[self.max_backups:]
                
                for backup in backups_to_delete:
                    # Delete backup file
                    file_path = os.path.join(self.backup_dir, backup.file_name)
                    zip_path = file_path.replace('.json', '.zip')
                    
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        if os.path.exists(zip_path):
                            os.remove(zip_path)
                    except OSError:
                        pass  
                    
                    db.delete(backup)
                
                db.commit()
                
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
    
    def get_backup_schedule_options(self) -> Dict[str, Any]:
        """Get available backup schedule options"""
        return {
            'daily': {
                'description': 'Backup once per day',
                'recommended': True,
                'retention_days': 30
            },
            'weekly': {
                'description': 'Backup once per week',
                'recommended': False,
                'retention_days': 90
            },
            'monthly': {
                'description': 'Backup once per month',
                'recommended': False,
                'retention_days': 365
            },
            'manual': {
                'description': 'Only on manual trigger',
                'recommended': False,
                'retention_days': 0
            }
        }
    
    def validate_backup_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a backup file"""
        try:
            data = crud_backup_restore.load_backup_file(file_path)
            if not data:
                return {'valid': False, 'error': 'Cannot read backup file'}
            
            if 'metadata' not in data:
                return {'valid': False, 'error': 'Missing metadata in backup file'}
            
            required_tables = ['customers', 'plans', 'transactions', 'metadata']
            missing_tables = [table for table in required_tables if table not in data]
            
            if missing_tables:
                return {'valid': False, 'error': f'Missing required tables: {missing_tables}'}
            
            return {
                'valid': True,
                'backup_timestamp': data['metadata'].get('backup_timestamp'),
                'data_version': data['metadata'].get('data_version'),
                'record_counts': {k: v for k, v in data['metadata'].items() if k != 'backup_timestamp' and k != 'data_version'}
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

backup_service = BackupService()