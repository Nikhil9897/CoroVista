"""
Shared pytest fixtures for CoroVista Backend API tests
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from ml.preprocessing.pipeline import extract_features_and_targets, load_dataset

RAW_DATA_PATH = Path("data/raw/extention of Z-Alizadeh sani dataset.xlsx")


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Returns FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="session")
def valid_patient_dict() -> dict:
    """Returns a valid patient dictionary from raw dataset row 0."""
    df_raw = load_dataset(RAW_DATA_PATH)
    X_raw, _ = extract_features_and_targets(df_raw)
    return X_raw.iloc[0].to_dict()
