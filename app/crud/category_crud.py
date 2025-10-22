from sqlalchemy.orm import Session
from app.models.category import Category

class CategoryCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: int) -> Category:
        return self.db.query(Category).filter(Category.category_id == category_id).first()
    
    def get_by_name(self, category_name: str) -> Category:
        return self.db.query(Category).filter(Category.category_name == category_name).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Category).offset(skip).limit(limit).all()
    
    def create(self, category_data: dict) -> Category:
        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def update(self, category_id: int, category_data: dict) -> Category:
        category = self.get_by_id(category_id)
        if category:
            for key, value in category_data.items():
                setattr(category, key, value)
            self.db.commit()
            self.db.refresh(category)
        return category
    
    def delete(self, category_id: int) -> bool:
        category = self.get_by_id(category_id)
        if category:
            self.db.delete(category)
            self.db.commit()
            return True
        return False