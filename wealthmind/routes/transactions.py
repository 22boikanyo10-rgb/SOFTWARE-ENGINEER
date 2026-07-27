"""API routes for transaction management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import List, Optional

from wealthmind.schemas import TransactionCreate, TransactionResponse
from wealthmind.models import User, Transaction, BankAccount
from wealthmind.database import get_db
from wealthmind.security import SecurityManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


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


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> Transaction:
    """Create a new transaction.

    Args:
        transaction_data: Transaction creation data
        authorization: Bearer token
        db: Database session

    Returns:
        Created transaction

    Raises:
        HTTPException: If account not found or unauthorized
    """
    user = get_current_user_from_token(authorization, db)
    
    # Verify account belongs to user
    account = db.query(BankAccount).filter(
        (BankAccount.id == transaction_data.account_id) & (BankAccount.user_id == user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    # Create transaction
    db_transaction = Transaction(
        user_id=user.id,
        account_id=transaction_data.account_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        category=transaction_data.category,
        description=transaction_data.description,
        merchant_name=transaction_data.merchant_name,
        transaction_date=transaction_data.transaction_date,
        is_recurring=transaction_data.is_recurring,
        tags=transaction_data.tags
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    logger.info(f"Transaction created for user {user.id}: {db_transaction.id}")
    return db_transaction


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    authorization: str = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
) -> List[Transaction]:
    """List transactions for current user with optional filters.

    Args:
        authorization: Bearer token
        skip: Number of transactions to skip
        limit: Number of transactions to return
        account_id: Filter by account ID
        category: Filter by category
        start_date: Filter transactions after this date
        end_date: Filter transactions before this date
        db: Database session

    Returns:
        List of transactions
    """
    user = get_current_user_from_token(authorization, db)
    
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
) -> Transaction:
    """Get a specific transaction.

    Args:
        transaction_id: Transaction ID
        authorization: Bearer token
        db: Database session

    Returns:
        Transaction details

    Raises:
        HTTPException: If transaction not found or unauthorized
    """
    user = get_current_user_from_token(authorization, db)
    
    transaction = db.query(Transaction).filter(
        (Transaction.id == transaction_id) & (Transaction.user_id == user.id)
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.get("/analytics/summary", response_model=dict)
async def get_transaction_summary(
    authorization: str = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> dict:
    """Get transaction summary for the last N days.

    Args:
        authorization: Bearer token
        days: Number of days to analyze
        db: Database session

    Returns:
        Summary statistics
    """
    user = get_current_user_from_token(authorization, db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        (Transaction.user_id == user.id) & (Transaction.transaction_date >= start_date)
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == "expense")
    total_transfers = sum(t.amount for t in transactions if t.transaction_type == "transfer")
    
    # Group by category
    category_breakdown = {}
    for transaction in transactions:
        if transaction.transaction_type == "expense":
            category = transaction.category
            if category not in category_breakdown:
                category_breakdown[category] = 0
            category_breakdown[category] += transaction.amount
    
    return {
        "period_days": days,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_transfers": total_transfers,
        "net_income": total_income - total_expenses,
        "transaction_count": len(transactions),
        "category_breakdown": category_breakdown
    }
