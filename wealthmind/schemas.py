"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# ============================================================================
# User Schemas
# ============================================================================

class UserRole(str, Enum):
    """User role enumeration."""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ADMIN = "admin"


class UserRegisterRequest(BaseModel):
    """User registration request schema."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=8, max_length=255, description="Password")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User response schema."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user verified")
    subscription_tier: str = Field(..., description="Subscription tier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


# ============================================================================
# Bank Account Schemas
# ============================================================================

class BankAccountCreate(BaseModel):
    """Create bank account request schema."""
    account_name: str = Field(..., min_length=1, max_length=100, description="Account name")
    account_type: str = Field(..., description="Account type")
    account_number: str = Field(..., description="Account number")
    bank_name: str = Field(..., description="Bank name")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Currency code")
    balance: float = Field(default=0.0, ge=0, description="Initial balance")


class BankAccountUpdate(BaseModel):
    """Update bank account request schema."""
    account_name: Optional[str] = Field(None, description="Account name")
    balance: Optional[float] = Field(None, ge=0, description="Account balance")
    is_active: Optional[bool] = Field(None, description="Is account active")


class BankAccountResponse(BaseModel):
    """Bank account response schema."""
    id: int = Field(..., description="Account ID")
    user_id: int = Field(..., description="User ID")
    account_name: str = Field(..., description="Account name")
    account_type: str = Field(..., description="Account type")
    account_number: str = Field(..., description="Account number")
    bank_name: str = Field(..., description="Bank name")
    balance: float = Field(..., description="Current balance")
    currency: str = Field(..., description="Currency")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionCategory(str, Enum):
    """Transaction category enumeration."""
    INCOME = "income"
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    EDUCATION = "education"
    PERSONAL = "personal"
    OTHER = "other"


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionCreate(BaseModel):
    """Create transaction request schema."""
    account_id: int = Field(..., description="Bank account ID")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    amount: float = Field(..., gt=0, description="Transaction amount")
    category: TransactionCategory = Field(..., description="Transaction category")
    description: str = Field(..., min_length=1, max_length=500, description="Description")
    merchant_name: Optional[str] = Field(None, max_length=100, description="Merchant name")
    transaction_date: datetime = Field(..., description="Transaction date")
    is_recurring: bool = Field(default=False, description="Is recurring")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class TransactionResponse(BaseModel):
    """Transaction response schema."""
    id: int = Field(..., description="Transaction ID")
    user_id: int = Field(..., description="User ID")
    account_id: int = Field(..., description="Account ID")
    transaction_type: str = Field(..., description="Transaction type")
    amount: float = Field(..., description="Amount")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="Description")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    transaction_date: datetime = Field(..., description="Transaction date")
    is_recurring: bool = Field(..., description="Is recurring")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Budget Schemas
# ============================================================================

class BudgetCreate(BaseModel):
    """Create budget request schema."""
    category: TransactionCategory = Field(..., description="Budget category")
    limit_amount: float = Field(..., gt=0, description="Budget limit")
    period: str = Field(default="monthly", description="Budget period")
    alert_threshold: float = Field(default=80.0, ge=0, le=100, description="Alert threshold percentage")
    start_date: datetime = Field(default_factory=datetime.utcnow, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


class BudgetResponse(BaseModel):
    """Budget response schema."""
    id: int = Field(..., description="Budget ID")
    user_id: int = Field(..., description="User ID")
    category: str = Field(..., description="Category")
    limit_amount: float = Field(..., description="Limit amount")
    spent_amount: float = Field(..., description="Spent amount")
    period: str = Field(..., description="Period")
    alert_threshold: float = Field(..., description="Alert threshold")
    is_active: bool = Field(..., description="Is active")
    percentage_used: float = Field(..., description="Percentage of budget used")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Financial Goal Schemas
# ============================================================================

class FinancialGoalCreate(BaseModel):
    """Create financial goal request schema."""
    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(None, max_length=1000, description="Goal description")
    target_amount: float = Field(..., gt=0, description="Target amount")
    target_date: datetime = Field(..., description="Target date")
    priority: str = Field(default="medium", description="Priority level")
    category: Optional[str] = Field(None, description="Goal category")


class FinancialGoalResponse(BaseModel):
    """Financial goal response schema."""
    id: int = Field(..., description="Goal ID")
    user_id: int = Field(..., description="User ID")
    title: str = Field(..., description="Title")
    description: Optional[str] = Field(None, description="Description")
    target_amount: float = Field(..., description="Target amount")
    current_amount: float = Field(..., description="Current amount")
    target_date: datetime = Field(..., description="Target date")
    priority: str = Field(..., description="Priority")
    category: Optional[str] = Field(None, description="Category")
    is_active: bool = Field(..., description="Is active")
    is_completed: bool = Field(..., description="Is completed")
    progress_percentage: float = Field(..., description="Progress percentage")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# AI Insight Schemas
# ============================================================================

class AIInsightResponse(BaseModel):
    """AI insight response schema."""
    id: int = Field(..., description="Insight ID")
    user_id: int = Field(..., description="User ID")
    insight_type: str = Field(..., description="Insight type")
    title: str = Field(..., description="Insight title")
    content: str = Field(..., description="Insight content")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    recommendation: Optional[str] = Field(None, description="Recommendation")
    is_actionable: bool = Field(..., description="Is actionable")
    is_read: bool = Field(..., description="Is read")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Error Response Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response schema."""
    status: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class ValidationError(BaseModel):
    """Validation error schema."""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
