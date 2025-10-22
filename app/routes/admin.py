from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_password_hash, verify_token, create_access_token
from app.models.user import User
from app.schemas.user import UserCreateAdmin, UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# Dependency to check if user is admin
def get_current_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_email = token.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user

@router.post("/register", response_model=UserResponse)
def register_admin(
    user_data: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Register a new admin user (only accessible by existing admins)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new admin user
    hashed_password = get_password_hash(user_data.password)
    admin_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get all users (admin only)
    """
    users = db.query(User).all()
    return users

@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Toggle user active status (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"User active status set to {user.is_active}"}