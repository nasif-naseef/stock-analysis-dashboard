"""
Stock Analysis API - Main Application Entry Point
"""
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, get_db
from app.tasks.scheduler import (
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
    trigger_manual_collection,
)
from app.services.data_collection_service import data_collection_service

# Import API routers
from app.api import (
    current_data_router,
    history_router,
    comparison_router,
    collection_router,
    dashboard_router,
    config_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    logger.info(f"Tracking tickers: {settings.TICKERS}")
    
    # Initialize database
    db_initialized = False
    try:
        init_db()
        logger.info("Database initialized")
        db_initialized = True
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.warning("Application will continue without database connection")
    
    # Start scheduler if database is available
    if db_initialized:
        try:
            start_scheduler(run_initial=settings.RUN_INITIAL_COLLECTION)
            logger.info("Scheduler started")
        except Exception as e:
            logger.warning(f"Scheduler initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Stop scheduler
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.warning(f"Error stopping scheduler: {e}")
    
    # Close data collection service
    try:
        data_collection_service.close()
        logger.info("Data collection service closed")
    except Exception as e:
        logger.warning(f"Error closing data collection service: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated stock data collection and analysis API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(current_data_router)
app.include_router(history_router)
app.include_router(comparison_router)
app.include_router(collection_router)
app.include_router(dashboard_router)
app.include_router(config_router)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# ============================================
# Data Collection Endpoints
# ============================================

@app.get("/api/v1/collection/status")
async def get_collection_status():
    """
    Get current data collection scheduler status.
    
    Returns information about:
    - Scheduler running state
    - Scheduled jobs and their next run times
    - Last collection results
    """
    return get_scheduler_status()


@app.post("/api/v1/collection/trigger")
async def trigger_collection(
    ticker: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger manual data collection.
    
    - If ticker is provided, collects data for that specific ticker
    - If ticker is None, collects data for all configured tickers
    
    The collection runs in the background and returns immediately.
    Use the /status endpoint to check progress.
    """
    if ticker:
        # Validate ticker
        ticker = ticker.upper().strip()
        if ticker not in settings.ticker_list:
            raise HTTPException(
                status_code=400,
                detail=f"Ticker {ticker} is not in configured tickers: {settings.ticker_list}"
            )
    
    # Run collection in background
    background_tasks.add_task(trigger_manual_collection, ticker)
    
    return {
        "status": "triggered",
        "message": f"Data collection started for {ticker or 'all tickers'}",
        "check_status_at": "/api/v1/collection/status"
    }


@app.post("/api/v1/collection/collect/{ticker}")
async def collect_ticker_data(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Collect all data types for a specific ticker synchronously.
    
    This endpoint waits for the collection to complete and returns the results.
    For large collections, use the /trigger endpoint instead.
    """
    ticker = ticker.upper().strip()
    
    try:
        result = data_collection_service.collect_all_data_for_ticker(ticker, db)
        return result
    except Exception as e:
        logger.error(f"Error collecting data for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect data: {str(e)}"
        )


@app.get("/api/v1/collection/tickers")
async def get_configured_tickers():
    """
    Get list of configured tickers for data collection.
    """
    return {
        "tickers": settings.ticker_list,
        "ticker_configs": settings.TICKER_CONFIGS
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
