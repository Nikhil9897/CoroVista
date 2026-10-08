"""
CoroVista Backend - API Routes
"""
from backend.app.api.routes.explanation import router as explanation_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.metadata import router as metadata_router
from backend.app.api.routes.prediction import router as prediction_router

__all__ = [
    "explanation_router",
    "health_router",
    "metadata_router",
    "prediction_router",
]
