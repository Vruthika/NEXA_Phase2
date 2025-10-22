from sqlalchemy.orm import Session
from app.models.backup import Backup

class BackupCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, backup_id: int) -> Backup:
        return self.db.query(Backup).filter(Backup.backup_id == backup_id).first()
    
    def get_all(self):
        return self.db.query(Backup).all()
    
    def create(self, backup_data: dict) -> Backup:
        backup = Backup(**backup_data)
        self.db.add(backup)
        self.db.commit()
        self.db.refresh(backup)
        return backup
    
    def delete(self, backup_id: int) -> bool:
        backup = self.get_by_id(backup_id)
        if backup:
            self.db.delete(backup)
            self.db.commit()
            return True
        return False