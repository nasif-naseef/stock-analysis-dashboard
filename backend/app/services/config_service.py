"""
Configuration Service

This module provides a service for managing runtime configuration
including tickers and API keys. It supports reloading configurations
from the database without requiring application restart.
"""
import logging
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.configuration import TickerConfiguration, APIConfiguration
from app.schemas.config_schemas import (
    TickerConfigurationCreate,
    TickerConfigurationUpdate,
    APIConfigurationCreate,
    APIConfigurationUpdate,
    mask_api_key,
)
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)


@dataclass
class TickerConfig:
    """Runtime ticker configuration"""
    ticker: str
    exchange: str
    tr_v4_id: str
    tr_v3_id: str


class ConfigService:
    """
    Service for managing runtime configuration.
    
    Provides methods for:
    - Managing ticker configurations (CRUD operations)
    - Managing API key configurations (CRUD operations)
    - Runtime configuration caching and reloading
    - API key masking for security
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._ticker_cache: Dict[str, TickerConfig] = {}
        self._api_key_cache: Dict[str, str] = {}
        self._last_reload: Optional[datetime] = None
    
    # ============================================
    # Ticker Configuration Methods
    # ============================================
    
    def get_all_tickers(self, db: Session, include_inactive: bool = False) -> List[TickerConfiguration]:
        """Get all ticker configurations from database"""
        query = db.query(TickerConfiguration)
        if not include_inactive:
            query = query.filter(TickerConfiguration.is_active == True)
        return query.order_by(TickerConfiguration.ticker).all()
    
    def get_ticker(self, db: Session, ticker: str) -> Optional[TickerConfiguration]:
        """Get a specific ticker configuration by ticker symbol"""
        ticker = ticker.strip().upper()
        return db.query(TickerConfiguration).filter(
            TickerConfiguration.ticker == ticker
        ).first()
    
    def get_ticker_by_id(self, db: Session, ticker_id: int) -> Optional[TickerConfiguration]:
        """Get a specific ticker configuration by ID"""
        return db.query(TickerConfiguration).filter(
            TickerConfiguration.id == ticker_id
        ).first()
    
    def create_ticker(
        self, 
        db: Session, 
        ticker_data: TickerConfigurationCreate
    ) -> TickerConfiguration:
        """Create a new ticker configuration"""
        ticker = TickerConfiguration(
            ticker=ticker_data.ticker,
            exchange=ticker_data.exchange,
            tr_v4_id=ticker_data.tr_v4_id,
            tr_v3_id=ticker_data.tr_v3_id,
            is_active=ticker_data.is_active,
            description=ticker_data.description,
        )
        db.add(ticker)
        db.commit()
        db.refresh(ticker)
        
        # Update cache
        self._update_ticker_cache(ticker)
        
        logger.info(f"Created ticker configuration: {ticker.ticker}")
        return ticker
    
    def update_ticker(
        self, 
        db: Session, 
        ticker: str, 
        ticker_data: TickerConfigurationUpdate
    ) -> Optional[TickerConfiguration]:
        """Update an existing ticker configuration"""
        ticker = ticker.strip().upper()
        db_ticker = self.get_ticker(db, ticker)
        if not db_ticker:
            return None
        
        # exclude_unset=True ensures we only get fields that were explicitly set
        update_data = ticker_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticker, field, value)
        
        db_ticker.updated_at = get_utc_now()
        db.commit()
        db.refresh(db_ticker)
        
        # Update cache
        self._update_ticker_cache(db_ticker)
        
        logger.info(f"Updated ticker configuration: {ticker}")
        return db_ticker
    
    def delete_ticker(self, db: Session, ticker: str) -> bool:
        """Delete a ticker configuration"""
        ticker = ticker.strip().upper()
        db_ticker = self.get_ticker(db, ticker)
        if not db_ticker:
            return False
        
        db.delete(db_ticker)
        db.commit()
        
        # Remove from cache
        with self._lock:
            self._ticker_cache.pop(ticker, None)
        
        logger.info(f"Deleted ticker configuration: {ticker}")
        return True
    
    # ============================================
    # API Configuration Methods
    # ============================================
    
    def get_all_api_configs(self, db: Session, include_inactive: bool = False) -> List[APIConfiguration]:
        """Get all API configurations from database"""
        query = db.query(APIConfiguration)
        if not include_inactive:
            query = query.filter(APIConfiguration.is_active == True)
        return query.order_by(APIConfiguration.service_name).all()
    
    def get_api_config(self, db: Session, service_name: str) -> Optional[APIConfiguration]:
        """Get a specific API configuration by service name"""
        service_name = service_name.strip().lower().replace(' ', '_')
        return db.query(APIConfiguration).filter(
            APIConfiguration.service_name == service_name
        ).first()
    
    def get_api_config_by_id(self, db: Session, config_id: int) -> Optional[APIConfiguration]:
        """Get a specific API configuration by ID"""
        return db.query(APIConfiguration).filter(
            APIConfiguration.id == config_id
        ).first()
    
    def create_api_config(
        self, 
        db: Session, 
        api_data: APIConfigurationCreate
    ) -> APIConfiguration:
        """Create a new API configuration"""
        api_config = APIConfiguration(
            service_name=api_data.service_name,
            api_key=api_data.api_key,
            description=api_data.description,
            is_active=api_data.is_active,
        )
        db.add(api_config)
        db.commit()
        db.refresh(api_config)
        
        # Update cache
        self._update_api_cache(api_config)
        
        logger.info(f"Created API configuration: {api_config.service_name}")
        return api_config
    
    def update_api_config(
        self, 
        db: Session, 
        service_name: str, 
        api_data: APIConfigurationUpdate
    ) -> Optional[APIConfiguration]:
        """Update an existing API configuration"""
        service_name = service_name.strip().lower().replace(' ', '_')
        db_api_config = self.get_api_config(db, service_name)
        if not db_api_config:
            return None
        
        # exclude_unset=True ensures we only get fields that were explicitly set
        update_data = api_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_api_config, field, value)
        
        db_api_config.updated_at = get_utc_now()
        db.commit()
        db.refresh(db_api_config)
        
        # Update cache
        self._update_api_cache(db_api_config)
        
        logger.info(f"Updated API configuration: {service_name}")
        return db_api_config
    
    # ============================================
    # Cache Management Methods
    # ============================================
    
    def reload_configuration(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Reload all configurations from database into cache.
        
        This method can be called to refresh the runtime configuration
        without restarting the application.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        
        try:
            with self._lock:
                # Reload ticker configurations
                tickers = self.get_all_tickers(db, include_inactive=False)
                self._ticker_cache.clear()
                for ticker in tickers:
                    self._ticker_cache[ticker.ticker] = TickerConfig(
                        ticker=ticker.ticker,
                        exchange=ticker.exchange or "",
                        tr_v4_id=ticker.tr_v4_id or "",
                        tr_v3_id=ticker.tr_v3_id or "",
                    )
                
                # Reload API configurations
                api_configs = self.get_all_api_configs(db, include_inactive=False)
                self._api_key_cache.clear()
                for api_config in api_configs:
                    self._api_key_cache[api_config.service_name] = api_config.api_key
                
                self._last_reload = get_utc_now()
            
            logger.info(f"Configuration reloaded: {len(self._ticker_cache)} tickers, {len(self._api_key_cache)} API keys")
            
            return {
                "status": "success",
                "tickers_loaded": len(self._ticker_cache),
                "api_keys_loaded": len(self._api_key_cache),
                "reload_time": self._last_reload.isoformat() if self._last_reload else None,
            }
        finally:
            if close_db:
                db.close()
    
    def _update_ticker_cache(self, ticker: TickerConfiguration) -> None:
        """Update a single ticker in the cache"""
        if ticker.is_active:
            with self._lock:
                self._ticker_cache[ticker.ticker] = TickerConfig(
                    ticker=ticker.ticker,
                    exchange=ticker.exchange or "",
                    tr_v4_id=ticker.tr_v4_id or "",
                    tr_v3_id=ticker.tr_v3_id or "",
                )
        else:
            with self._lock:
                self._ticker_cache.pop(ticker.ticker, None)
    
    def _update_api_cache(self, api_config: APIConfiguration) -> None:
        """Update a single API config in the cache"""
        if api_config.is_active:
            with self._lock:
                self._api_key_cache[api_config.service_name] = api_config.api_key
        else:
            with self._lock:
                self._api_key_cache.pop(api_config.service_name, None)
    
    # ============================================
    # Runtime Access Methods
    # ============================================
    
    def get_active_ticker_list(self) -> List[str]:
        """Get list of active ticker symbols from cache"""
        with self._lock:
            return list(self._ticker_cache.keys())
    
    def get_ticker_config(self, ticker: str) -> Optional[TickerConfig]:
        """Get ticker configuration from cache"""
        ticker = ticker.strip().upper()
        with self._lock:
            return self._ticker_cache.get(ticker)
    
    def get_ticker_configs_dict(self) -> Dict[str, Dict[str, str]]:
        """Get all ticker configurations as a dictionary (for compatibility)"""
        with self._lock:
            return {
                ticker: {
                    "exchange": config.exchange,
                    "tr_v4_id": config.tr_v4_id,
                    "tr_v3_id": config.tr_v3_id,
                }
                for ticker, config in self._ticker_cache.items()
            }
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for a service from cache"""
        service_name = service_name.strip().lower().replace(' ', '_')
        with self._lock:
            return self._api_key_cache.get(service_name)
    
    def get_configuration_status(self, db: Session) -> Dict[str, Any]:
        """Get current configuration status"""
        total_tickers = db.query(TickerConfiguration).count()
        active_tickers = db.query(TickerConfiguration).filter(
            TickerConfiguration.is_active == True
        ).count()
        total_api_keys = db.query(APIConfiguration).count()
        active_api_keys = db.query(APIConfiguration).filter(
            APIConfiguration.is_active == True
        ).count()
        
        return {
            "active_tickers": active_tickers,
            "total_tickers": total_tickers,
            "active_api_keys": active_api_keys,
            "total_api_keys": total_api_keys,
            "last_reload": self._last_reload,
        }
    
    # ============================================
    # Helper Methods
    # ============================================
    
    @staticmethod
    def mask_api_key_value(api_key: str) -> str:
        """Mask an API key for secure display"""
        return mask_api_key(api_key)


# Singleton instance
config_service = ConfigService()
