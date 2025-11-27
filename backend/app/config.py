"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Dict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "Stock Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://stockuser:stockpass@localhost:5432/stockdb"
    
    # API Tokens
    TRADING_CENTRAL_TOKEN: str = ""
    
    # Tickers Configuration
    TICKERS: str = "AAPL,TSLA,NVDA"
    
    # Individual ticker configurations
    TICKER_CONFIGS: Dict[str, Dict[str, str]] = {
        "AAPL": {
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00000ADA",
            "tr_v3_id": "US-123705"
        },
        "TSLA": {
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00004EP4",
            "tr_v3_id": "US-303648"
        },
        "NVDA": {
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00000BXN",
            "tr_v3_id": "US-124689"
        }
    }
    
    # Collection Settings
    COLLECTION_INTERVAL_HOURS: int = 1
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 60
    RUN_INITIAL_COLLECTION: bool = True
    
    # API Settings
    API_RATE_LIMIT: int = 100
    API_TIMEOUT: int = 10
    CACHE_TTL_SECONDS: int = 300
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # Features
    ENABLE_EMAIL_ALERTS: bool = False
    ENABLE_SLACK_NOTIFICATIONS: bool = False
    
    # Date Configuration
    HISTORICAL_DAYS: int = 5 * 365  # 5 years
    
    @property
    def ticker_list(self) -> List[str]:
        """Get list of tickers"""
        return [t.strip() for t in self.TICKERS.split(',')]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get list of CORS origins"""
        return [o.strip() for o in self.CORS_ORIGINS.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
