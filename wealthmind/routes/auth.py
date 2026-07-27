"""API routes for authentication."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from wealthmind.schemas import (
    UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
)
from wealthmind.security import SecurityManager
from wealthmind.models import User
from wealthmind.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
) -> User:
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered"
        )
    
    # Hash password and create user
    hashed_password = SecurityManager.hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User registered: {db_user.email}")
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
) -> dict:
    """Authenticate user and return tokens.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials invalid
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not SecurityManager.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = SecurityManager.create_access_token(data={"sub": str(user.id)})
    refresh_token = SecurityManager.create_refresh_token(data={"sub": str(user.id)})
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutes
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token: str,
    db: Session = Depends(get_db)
) -> dict:
    """Refresh access token using refresh token.

    Args:
        token: Refresh token
        db: Database session

    Returns:
        New access token

    Raises:
        HTTPException: If token invalid
    """
    token_data = SecurityManager.decode_token(token)
    
    if not token_data or not SecurityManager.verify_token_type(token_data, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = SecurityManager.create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": token,
        "token_type": "bearer",
        "expires_in": 30 * 60
    }
