"""
SQLAlchemy Models for Configuration Management

This module contains database models for managing:
- Ticker configurations (symbols, exchanges, API identifiers)
- API configurations (API keys for external services)
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Index
)
from app.database import Base
from app.utils.helpers import get_utc_now


class TickerConfiguration(Base):
    """
    Model for storing ticker configurations
    
    Contains ticker symbols and their associated configurations
    for data collection from various APIs.
    """
    __tablename__ = "ticker_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, unique=True, index=True)
    exchange = Column(String(50), nullable=False, default="NASDAQ")
    
    # Trading Central API identifiers
    tr_v4_id = Column(String(50), nullable=True)  # e.g., "EQ-0C00000ADA"
    tr_v3_id = Column(String(50), nullable=True)  # e.g., "US-123705"
    
    # Configuration metadata
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    
    __table_args__ = (
        Index('ix_ticker_configurations_ticker_active', 'ticker', 'is_active'),
    )


class APIConfiguration(Base):
    """
    Model for storing API key configurations
    
    Contains API keys and tokens for external services used by the application.
    API keys are stored encrypted/hashed and masked in responses.
    """
    __tablename__ = "api_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False, unique=True, index=True)
    api_key = Column(Text, nullable=False)  # The actual API key value
    
    # Configuration metadata
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    
    __table_args__ = (
        Index('ix_api_configurations_service_active', 'service_name', 'is_active'),
    )
