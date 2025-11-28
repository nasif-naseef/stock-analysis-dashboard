"""
Database Connection and Session Management
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database(db: Session) -> dict:
    """
    Seed database with initial ticker and API configurations.
    
    This function is called after database tables are created to ensure
    default configurations are available for the application to work properly.
    
    Returns:
        dict: Summary of seeding results
    """
    # Import models here to avoid circular imports
    from app.models.configuration import TickerConfiguration, APIConfiguration
    
    results = {
        "tickers_created": 0,
        "api_keys_created": 0,
        "errors": []
    }
    
    # Default tickers from settings
    default_tickers = [
        {
            "ticker": "AAPL",
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00000ADA",
            "tr_v3_id": "US-123705",
            "description": "Apple Inc."
        },
        {
            "ticker": "TSLA",
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00004EP4",
            "tr_v3_id": "US-303648",
            "description": "Tesla, Inc."
        },
        {
            "ticker": "NVDA",
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00000BXN",
            "tr_v3_id": "US-124689",
            "description": "NVIDIA Corporation"
        },
        {
            "ticker": "GOOGL",
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00002XX4",
            "tr_v3_id": "US-129479",
            "description": "Alphabet Inc. Class A"
        },
        {
            "ticker": "MSFT",
            "exchange": "NASDAQ",
            "tr_v4_id": "EQ-0C00000D3H",
            "tr_v3_id": "US-124040",
            "description": "Microsoft Corporation"
        },
    ]
    
    # Seed default tickers
    for ticker_data in default_tickers:
        try:
            # Check if ticker already exists
            existing = db.query(TickerConfiguration).filter(
                TickerConfiguration.ticker == ticker_data["ticker"]
            ).first()
            
            if not existing:
                ticker = TickerConfiguration(
                    ticker=ticker_data["ticker"],
                    exchange=ticker_data["exchange"],
                    tr_v4_id=ticker_data["tr_v4_id"],
                    tr_v3_id=ticker_data["tr_v3_id"],
                    description=ticker_data["description"],
                    is_active=True
                )
                db.add(ticker)
                results["tickers_created"] += 1
                logger.info(f"Seeded ticker: {ticker_data['ticker']}")
        except Exception as e:
            results["errors"].append(f"Failed to seed ticker {ticker_data['ticker']}: {str(e)}")
            logger.error(f"Error seeding ticker {ticker_data['ticker']}: {e}")
    
    # Default API configurations (placeholders)
    default_api_configs = [
        {
            "service_name": "trading_central",
            "api_key": "",  # Empty placeholder - must be configured by admin
            "description": "Trading Central API for market data and analysis"
        },
    ]
    
    # Seed default API configurations
    for api_data in default_api_configs:
        try:
            # Check if API config already exists
            existing = db.query(APIConfiguration).filter(
                APIConfiguration.service_name == api_data["service_name"]
            ).first()
            
            if not existing:
                api_config = APIConfiguration(
                    service_name=api_data["service_name"],
                    api_key=api_data["api_key"],
                    description=api_data["description"],
                    is_active=True
                )
                db.add(api_config)
                results["api_keys_created"] += 1
                logger.info(f"Seeded API config: {api_data['service_name']}")
        except Exception as e:
            results["errors"].append(f"Failed to seed API config {api_data['service_name']}: {str(e)}")
            logger.error(f"Error seeding API config {api_data['service_name']}: {e}")
    
    try:
        db.commit()
        logger.info(f"Database seeding completed: {results['tickers_created']} tickers, {results['api_keys_created']} API configs")
    except Exception as e:
        db.rollback()
        results["errors"].append(f"Failed to commit: {str(e)}")
        logger.error(f"Error committing seed data: {e}")
    
    return results


def init_db():
    """Initialize database - create all tables and seed with default data"""
    Base.metadata.create_all(bind=engine)
    
    # Seed database with default configurations
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
