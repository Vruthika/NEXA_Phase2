from sqlalchemy.orm import Session
from app.models.models import Category
from app.schemas.category import CategoryCreate

class CRUDCategory:
    def get(self, db: Session, category_id: int):
        return db.query(Category).filter(Category.category_id == category_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Category).offset(skip).limit(limit).all()
    
    def create(self, db: Session, category: CategoryCreate):
        db_category = Category(category_name=category.category_name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def update(self, db: Session, category_id: int, category_name: str):
        db_category = self.get(db, category_id)
        if db_category:
            db_category.category_name = category_name
            db.commit()
            db.refresh(db_category)
        return db_category
    
    def delete(self, db: Session, category_id: int):
        db_category = self.get(db, category_id)
        if db_category:
            db.delete(db_category)
            db.commit()
        return db_category

crud_category = CRUDCategory()