"""SQLAlchemy ORM models for WealthMind."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, 
    Text, Enum, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration."""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ADMIN = "admin"


class TransactionCategory(str, enum.Enum):
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


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
        Index('ix_users_email', 'email'),
        Index('ix_users_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.FREE)
    
    # Profile
    profile_picture_url = Column(String(500))
    bio = Column(Text)
    
    # Subscription
    subscription_tier = Column(Enum(UserRole), default=UserRole.FREE)
    subscription_start_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    stripe_customer_id = Column(String(255), unique=True)
    
    # Preferences
    currency = Column(String(3), default="USD")
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("AIInsight", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class BankAccount(Base):
    """Bank account model for tracking multiple accounts."""

    __tablename__ = "bank_accounts"
    __table_args__ = (
        Index('ix_bank_accounts_user_id', 'user_id'),
        Index('ix_bank_accounts_account_number', 'account_number'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50))  # Checking, Savings, Credit Card, etc.
    account_number = Column(String(100), nullable=False)
    bank_name = Column(String(100))
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    """Transaction model for income/expense tracking."""

    __tablename__ = "transactions"
    __table_args__ = (
        Index('ix_transactions_user_id', 'user_id'),
        Index('ix_transactions_account_id', 'account_id'),
        Index('ix_transactions_date', 'transaction_date'),
        Index('ix_transactions_category', 'category'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Enum(TransactionCategory), nullable=False)
    description = Column(String(500))
    merchant_name = Column(String(100))
    transaction_date = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("BankAccount", back_populates="transactions")


class Budget(Base):
    """Budget model for spending limits."""

    __tablename__ = "budgets"
    __table_args__ = (
        Index('ix_budgets_user_id', 'user_id'),
        Index('ix_budgets_category', 'category'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(Enum(TransactionCategory), nullable=False)
    limit_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)
    period = Column(String(20), default="monthly")  # daily, weekly, monthly, yearly
    alert_threshold = Column(Float, default=80.0)  # Alert at 80% of budget
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")


class FinancialGoal(Base):
    """Financial goal model for savings targets."""

    __tablename__ = "financial_goals"
    __table_args__ = (
        Index('ix_financial_goals_user_id', 'user_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high
    category = Column(String(100))  # Vacation, House, Education, etc.
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")


class AIInsight(Base):
    """AI-generated insights model."""

    __tablename__ = "ai_insights"
    __table_args__ = (
        Index('ix_ai_insights_user_id', 'user_id'),
        Index('ix_ai_insights_created_at', 'created_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    insight_type = Column(String(50), nullable=False)  # spending_pattern, savings_opportunity, forecast, etc.
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.5)  # 0-1 confidence
    recommendation = Column(Text)
    is_actionable = Column(Boolean, default=True)
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="insights")


class AuditLog(Base):
    """Audit log for tracking user actions."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('ix_audit_logs_user_id', 'user_id'),
        Index('ix_audit_logs_action', 'action'),
        Index('ix_audit_logs_timestamp', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))  # User, Transaction, Budget, etc.
    resource_id = Column(Integer)
    details = Column(Text)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    status = Column(String(20), default="success")  # success, failure
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
