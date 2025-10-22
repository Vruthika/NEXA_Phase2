from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.linked_account_crud import LinkedAccountCRUD
from app.crud.customer_crud import CustomerCRUD
from app.schemas.linked_account import LinkedAccountCreate

class LinkedAccountService:
    def __init__(self, db: Session):
        self.db = db
        self.linked_account_crud = LinkedAccountCRUD(db)
        self.customer_crud = CustomerCRUD(db)
    
    def create_linked_account(self, primary_customer_id: int, linked_account_data: LinkedAccountCreate):
        # Verify primary customer exists
        primary_customer = self.customer_crud.get_by_id(primary_customer_id)
        if not primary_customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Primary customer not found"
            )
        
        # Check if linked customer exists (if provided)
        if linked_account_data.linked_customer_id:
            linked_customer = self.customer_crud.get_by_id(linked_account_data.linked_customer_id)
            if not linked_customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked customer not found"
                )
        
        # Check if link already exists
        existing_link = self.linked_account_crud.get_by_primary_and_phone(
            primary_customer_id,
            linked_account_data.linked_phone_number
        )
        if existing_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already linked to this phone number"
            )
        
        # Create linked account
        linked_account_dict = linked_account_data.dict()
        linked_account_dict["primary_customer_id"] = primary_customer_id
        
        return self.linked_account_crud.create(linked_account_dict)
    
    def get_linked_accounts_by_primary(self, primary_customer_id: int):
        customer = self.customer_crud.get_by_id(primary_customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.linked_account_crud.get_by_primary_customer(primary_customer_id)
    
    def get_linked_accounts_by_linked(self, linked_customer_id: int):
        customer = self.customer_crud.get_by_id(linked_customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.linked_account_crud.get_by_linked_customer(linked_customer_id)
    
    def delete_linked_account(self, linked_account_id: int, primary_customer_id: int):
        linked_account = self.linked_account_crud.get_by_id(linked_account_id)
        if not linked_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked account not found"
            )
        
        # Verify the primary customer owns this linked account
        if linked_account.primary_customer_id != primary_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this linked account"
            )
        
        return self.linked_account_crud.delete(linked_account_id)