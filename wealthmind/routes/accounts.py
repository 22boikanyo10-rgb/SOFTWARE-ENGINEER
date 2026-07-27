"""API routes for bank account management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import List

from wealthmind.schemas import BankAccountCreate, BankAccountUpdate, BankAccountResponse
from wealthmind.models import User, BankAccount
from wealthmind.database import get_db
from wealthmind.security import SecurityManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Bank Accounts"])


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


@router.post("", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: BankAccountCreate,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> BankAccount:
    """Create a new bank account.

    Args:
        account_data: Account creation data
        authorization: Bearer token
        db: Database session

    Returns:
        Created bank account
    """
    user = get_current_user_from_token(authorization, db)
    
    db_account = BankAccount(
        user_id=user.id,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        account_number=account_data.account_number,
        bank_name=account_data.bank_name,
        balance=account_data.balance,
        currency=account_data.currency
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    logger.info(f"Bank account created for user {user.id}: {db_account.account_name}")
    return db_account


@router.get("", response_model=List[BankAccountResponse])
async def list_accounts(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> List[BankAccount]:
    """List all bank accounts for current user.

    Args:
        authorization: Bearer token
        db: Database session

    Returns:
        List of user's bank accounts
    """
    user = get_current_user_from_token(authorization, db)
    
    accounts = db.query(BankAccount).filter(BankAccount.user_id == user.id).all()
    return accounts


@router.get("/{account_id}", response_model=BankAccountResponse)
async def get_account(
    account_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> BankAccount:
    """Get a specific bank account.

    Args:
        account_id: Account ID
        authorization: Bearer token
        db: Database session

    Returns:
        Bank account details

    Raises:
        HTTPException: If account not found or unauthorized
    """
    user = get_current_user_from_token(authorization, db)
    
    account = db.query(BankAccount).filter(
        (BankAccount.id == account_id) & (BankAccount.user_id == user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    return account


@router.put("/{account_id}", response_model=BankAccountResponse)
async def update_account(
    account_id: int,
    account_data: BankAccountUpdate,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> BankAccount:
    """Update a bank account.

    Args:
        account_id: Account ID
        account_data: Update data
        authorization: Bearer token
        db: Database session

    Returns:
        Updated bank account

    Raises:
        HTTPException: If account not found or unauthorized
    """
    user = get_current_user_from_token(authorization, db)
    
    account = db.query(BankAccount).filter(
        (BankAccount.id == account_id) & (BankAccount.user_id == user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    # Update fields
    update_data = account_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    logger.info(f"Bank account updated for user {user.id}: {account.id}")
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> None:
    """Delete a bank account.

    Args:
        account_id: Account ID
        authorization: Bearer token
        db: Database session

    Raises:
        HTTPException: If account not found or unauthorized
    """
    user = get_current_user_from_token(authorization, db)
    
    account = db.query(BankAccount).filter(
        (BankAccount.id == account_id) & (BankAccount.user_id == user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    db.delete(account)
    db.commit()
    
    logger.info(f"Bank account deleted for user {user.id}: {account_id}")
