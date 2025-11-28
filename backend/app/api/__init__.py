"""
API Routes Package
"""
from app.api.current_data import router as current_data_router
from app.api.history import router as history_router
from app.api.comparison import router as comparison_router
from app.api.collection import router as collection_router
from app.api.dashboard import router as dashboard_router
from app.api.config import router as config_router

__all__ = [
    "current_data_router",
    "history_router",
    "comparison_router",
    "collection_router",
    "dashboard_router",
    "config_router",
]
