from sqlalchemy.orm import Session
from app.models.restore import Restore

class RestoreCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, restore_id: int) -> Restore:
        return self.db.query(Restore).filter(Restore.restore_id == restore_id).first()
    
    def get_all(self):
        return self.db.query(Restore).all()
    
    def create(self, restore_data: dict) -> Restore:
        restore = Restore(**restore_data)
        self.db.add(restore)
        self.db.commit()
        self.db.refresh(restore)
        return restore