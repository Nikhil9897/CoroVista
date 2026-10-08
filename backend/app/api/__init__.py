"""
CoroVista Backend - Main API Router
"""

from fastapi import APIRouter
from backend.app.api.routes.explanation import router as explanation_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.metadata import router as metadata_router
from backend.app.api.routes.prediction import router as prediction_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(metadata_router)
api_router.include_router(prediction_router)
api_router.include_router(explanation_router)

__all__ = ["api_router"]
