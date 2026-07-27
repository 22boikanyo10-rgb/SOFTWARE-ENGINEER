"""Application configuration."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App Settings
    app_name: str = Field(default="WealthMind", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode")
    version: str = Field(default="0.1.0", description="App version")

    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")

    # Database Settings
    database_url: str = Field(
        default="sqlite:///./wealthmind.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Log SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database connection pool overflow")

    # Security Settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT encoding"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")

    # Subscription Settings
    stripe_secret_key: Optional[str] = Field(default=None, description="Stripe API secret key")
    stripe_publishable_key: Optional[str] = Field(default=None, description="Stripe API publishable key")

    # AI/ML Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    enable_ai_insights: bool = Field(default=True, description="Enable AI-powered insights")

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # CORS Settings
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
