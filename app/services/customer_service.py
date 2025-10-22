from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.customer_crud import CustomerCRUD
from app.schemas.customer import CustomerUpdate

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_crud = CustomerCRUD(db)
    
    def get_customer_by_id(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer
    
    def update_customer(self, customer_id: int, customer_data: CustomerUpdate):
        customer = self.get_customer_by_id(customer_id)
        return self.customer_crud.update(customer_id, customer_data.dict(exclude_unset=True))
    
    def delete_customer(self, customer_id: int):
        customer = self.get_customer_by_id(customer_id)
        return self.customer_crud.soft_delete(customer_id)
    
    def get_customer_transactions(self, customer_id: int):
        customer = self.get_customer_by_id(customer_id)
        return customer.transactions
    
    def get_customer_subscriptions(self, customer_id: int):
        customer = self.get_customer_by_id(customer_id)
        return customer.subscriptions