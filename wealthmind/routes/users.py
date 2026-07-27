"""API routes for user management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import List

from wealthmind.schemas import UserResponse, UserRegisterRequest
from wealthmind.models import User
from wealthmind.database import get_db
from wealthmind.security import SecurityManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


def get_current_user_from_token(authorization: str = None, db: Session = Depends(get_db)) -> User:
    """Extract current user from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    token_data = SecurityManager.decode_token(token)
    
    if not token_data or not SecurityManager.verify_token_type(token_data, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> User:
    """Get current user profile.

    Args:
        authorization: Bearer token from header
        db: Database session

    Returns:
        Current user profile
    """
    user = get_current_user_from_token(authorization, db)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> User:
    """Get user by ID (requires authentication).

    Args:
        user_id: User ID
        authorization: Bearer token
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: If user not found
    """
    # Verify user is authenticated
    _ = get_current_user_from_token(authorization, db)
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> List[User]:
    """List all users (paginated, requires authentication).

    Args:
        skip: Number of users to skip
        limit: Number of users to return
        authorization: Bearer token
        db: Database session

    Returns:
        List of users
    """
    # Verify user is authenticated
    _ = get_current_user_from_token(authorization, db)
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users
