"""
CoroVista Backend - Application Configuration
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

import os
from typing import List, Union
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    COROVISTA_ENV: str = Field(default="development", description="Environment: development, test, or production")
    COROVISTA_API_PREFIX: str = Field(default="/api/v1", description="API route prefix")
    COROVISTA_CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins",
    )
    COROVISTA_MODEL_DIR: str = Field(default="models", description="Path to serialized models directory")

    API_TITLE: str = "CoroVista API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "Cardiovascular Risk Visualization & Multi-Target Prediction API.\n\n"
        "Provides multi-target coronary artery disease inference (Cath, LAD, LCX, RCA), "
        "Platt-calibrated risk probabilities, and local SHAP model-score explainability."
    )

    CLINICAL_DISCLAIMER: str = (
        "Educational and decision-support prototype only. Model predictions are not a diagnosis "
        "and do not replace clinical judgment, formal angiography, or diagnostic imaging."
    )

    VISUALIZATION_NOTE: str = (
        "Predicted vessel probabilities represent model-estimated stenosis risk and are not "
        "physical 3D lesion coordinates."
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    def get_cors_origins(self) -> List[str]:
        """Parses CORS origins whether configured as a list or comma-separated string."""
        if isinstance(self.COROVISTA_CORS_ORIGINS, list):
            return self.COROVISTA_CORS_ORIGINS
        if isinstance(self.COROVISTA_CORS_ORIGINS, str):
            return [orig.strip() for orig in self.COROVISTA_CORS_ORIGINS.split(",") if orig.strip()]
        return ["http://localhost:5173"]


settings = Settings()
