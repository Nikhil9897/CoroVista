"""
CoroVista Backend - FastAPI Application Entry Point
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.api import api_router
from backend.app.core.config import settings
from backend.app.core.errors import (
    CoroVistaAPIException,
    corovista_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
    value_error_handler,
)
from src.corovista.inference.loader import load_all_models

logger = logging.getLogger("corovista.backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eagerly loads and verifies models on startup."""
    logger.info("Initializing CoroVista API service...")
    try:
        models = load_all_models()
        logger.info(f"Successfully loaded {len(models)} model pipelines on startup: {list(models.keys())}")
    except Exception as e:
        logger.error(f"Failed to pre-load model pipelines on startup: {e}")
    yield
    logger.info("Shutting down CoroVista API service...")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Configure CORS
    origins = settings.get_cors_origins()
    logger.info(f"Configuring CORS origins: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Register Exception Handlers
    app.add_exception_handler(CoroVistaAPIException, corovista_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # 3. Mount API Routers
    app.include_router(api_router, prefix=settings.COROVISTA_API_PREFIX)

    # 4. Root redirect to interactive API documentation
    @app.get("/", include_in_schema=False)
    def root_redirect():
        return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
