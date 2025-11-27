"""
APScheduler Configuration for Automated Data Collection

This module configures and manages the scheduler for automated data collection jobs.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent

from app.config import settings
from app.database import SessionLocal
from app.services.data_collection_service import data_collection_service
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler(
    job_defaults={
        'coalesce': True,  # Run only once if multiple runs are missed
        'max_instances': 1,  # Only one instance of each job at a time
        'misfire_grace_time': 300  # 5 minute grace period for misfired jobs
    }
)

# Lock for thread-safe status updates
_status_lock = Lock()

# Track last collection results
_last_collection_result: Optional[Dict[str, Any]] = None
_last_collection_time: Optional[datetime] = None


def _job_listener(event: JobExecutionEvent) -> None:
    """
    Event listener for job execution events.
    
    Args:
        event: Job execution event
    """
    global _last_collection_result, _last_collection_time
    
    if event.job_id == 'collect_all_data':
        with _status_lock:
            _last_collection_time = get_utc_now()
            if event.exception:
                logger.error(f"Scheduled collection job failed: {event.exception}")
                _last_collection_result = {
                    "status": "error",
                    "error": str(event.exception)
                }
            else:
                logger.info("Scheduled collection job completed successfully")
                _last_collection_result = event.retval if event.retval else {"status": "success"}


def scheduled_collection_job() -> Dict[str, Any]:
    """
    Job that runs on schedule to collect data for all tickers.
    
    Returns:
        Collection results dictionary
    """
    logger.info("Starting scheduled data collection job")
    db = SessionLocal()
    try:
        result = data_collection_service.collect_all_tickers(db)
        return result
    except Exception as e:
        logger.error(f"Error in scheduled collection job: {e}")
        raise
    finally:
        db.close()


def scheduled_ticker_collection_job(ticker: str) -> Dict[str, Any]:
    """
    Job that runs on schedule to collect data for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Collection results dictionary
    """
    logger.info(f"Starting scheduled data collection for {ticker}")
    db = SessionLocal()
    try:
        result = data_collection_service.collect_all_data_for_ticker(ticker, db)
        return result
    except Exception as e:
        logger.error(f"Error in scheduled collection for {ticker}: {e}")
        raise
    finally:
        db.close()


def start_scheduler(run_initial: bool = True) -> None:
    """
    Start the scheduler with configured jobs.
    
    Args:
        run_initial: Whether to run an initial collection on startup
    """
    if scheduler.running:
        logger.warning("Scheduler is already running")
        return
    
    # Add event listener
    scheduler.add_listener(_job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    # Add main collection job with interval trigger
    interval_hours = settings.COLLECTION_INTERVAL_HOURS
    scheduler.add_job(
        scheduled_collection_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id='collect_all_data',
        name='Collect data for all tickers',
        replace_existing=True
    )
    
    logger.info(f"Added scheduled collection job with {interval_hours}h interval")
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Run initial collection if configured
    if run_initial and settings.RUN_INITIAL_COLLECTION:
        logger.info("Running initial data collection...")
        try:
            # Run initial collection in background
            scheduler.add_job(
                scheduled_collection_job,
                id='initial_collection',
                name='Initial data collection',
                replace_existing=True
            )
        except Exception as e:
            logger.error(f"Failed to run initial collection: {e}")


def stop_scheduler() -> None:
    """Stop the scheduler gracefully"""
    if not scheduler.running:
        logger.warning("Scheduler is not running")
        return
    
    logger.info("Stopping scheduler...")
    scheduler.shutdown(wait=True)
    logger.info("Scheduler stopped")


def get_scheduler_status() -> Dict[str, Any]:
    """
    Get current scheduler status and job information.
    
    Returns:
        Dictionary with scheduler status
    """
    with _status_lock:
        jobs = []
        if scheduler.running:
            for job in scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
        
        return {
            "running": scheduler.running,
            "jobs": jobs,
            "last_collection_time": _last_collection_time.isoformat() if _last_collection_time else None,
            "last_collection_result": _last_collection_result,
            "collection_interval_hours": settings.COLLECTION_INTERVAL_HOURS
        }


def trigger_manual_collection(ticker: Optional[str] = None) -> Dict[str, Any]:
    """
    Trigger a manual data collection.
    
    Args:
        ticker: Optional specific ticker to collect. If None, collects all tickers.
        
    Returns:
        Collection results dictionary
    """
    logger.info(f"Manual collection triggered for: {ticker or 'all tickers'}")
    
    db = SessionLocal()
    try:
        if ticker:
            result = data_collection_service.collect_all_data_for_ticker(ticker, db)
        else:
            result = data_collection_service.collect_all_tickers(db)
        
        # Update status
        with _status_lock:
            global _last_collection_result, _last_collection_time
            _last_collection_time = get_utc_now()
            _last_collection_result = result
        
        return result
    except Exception as e:
        logger.error(f"Error in manual collection: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def add_ticker_job(ticker: str, cron_expression: Optional[str] = None) -> bool:
    """
    Add a scheduled job for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        cron_expression: Optional cron expression for scheduling.
                        If None, uses the default interval.
        
    Returns:
        True if job was added successfully
    """
    try:
        job_id = f'collect_{ticker.upper()}'
        
        if cron_expression:
            trigger = CronTrigger.from_crontab(cron_expression)
        else:
            trigger = IntervalTrigger(hours=settings.COLLECTION_INTERVAL_HOURS)
        
        scheduler.add_job(
            scheduled_ticker_collection_job,
            trigger=trigger,
            args=[ticker],
            id=job_id,
            name=f'Collect data for {ticker}',
            replace_existing=True
        )
        
        logger.info(f"Added collection job for {ticker}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add job for {ticker}: {e}")
        return False


def remove_ticker_job(ticker: str) -> bool:
    """
    Remove a scheduled job for a specific ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if job was removed successfully
    """
    try:
        job_id = f'collect_{ticker.upper()}'
        scheduler.remove_job(job_id)
        logger.info(f"Removed collection job for {ticker}")
        return True
    except Exception as e:
        logger.error(f"Failed to remove job for {ticker}: {e}")
        return False


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get status of a specific job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Dictionary with job status or None if not found
    """
    try:
        job = scheduler.get_job(job_id)
        if job:
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
        return None
    except Exception:
        return None
