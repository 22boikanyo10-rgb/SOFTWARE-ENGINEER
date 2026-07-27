"""Dependency injection utilities."""

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from wealthmind.models import User
from wealthmind.security import SecurityManager
from wealthmind.database import get_db


async def get_current_user(
    token: str = Depends(lambda: None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token.

    Args:
        token: JWT token from request
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token invalid or user not found
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token_data = SecurityManager.decode_token(token)
    
    if not token_data or not SecurityManager.verify_token_type(token_data, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = token_data.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
