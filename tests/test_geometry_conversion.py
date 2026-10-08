"""
Tests for Stage 5B.2 geometry conversion and manifest verification.
"""

import os
import json
import pytest
from scripts.validate_converted_geometry import run_geometry_validation


def test_geometry_conversion_and_alignment():
    """Verify that all GLBs, bounds, junctions, and dimensions pass validation."""
    assert run_geometry_validation() is True


def test_manifest_metadata_integrity():
    manifest_path = os.path.join("assets", "anatomy", "bodyparts3d", "processed", "manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["metadata"]["license"] == "CC BY-SA 2.1 Japan"
    assert manifest["metadata"]["total_selected_source_objs"] == 14

    # Verify locked vessel targets
    assert "vessel_lad" in manifest["groups"]
    assert "vessel_lcx" in manifest["groups"]
    assert "vessel_rca" in manifest["groups"]

    # LAD segments MM420, MM424, MM425
    lad_segs = [s["id"] for s in manifest["groups"]["vessel_lad"]["segments"]]
    assert lad_segs == ["MM420", "MM424", "MM425"]

    # LCX segments MM426, MM635
    lcx_segs = [s["id"] for s in manifest["groups"]["vessel_lcx"]["segments"]]
    assert lcx_segs == ["MM426", "MM635"]

    # RCA segments MM556, MM436, MM439
    rca_segs = [s["id"] for s in manifest["groups"]["vessel_rca"]["segments"]]
    assert rca_segs == ["MM556", "MM436", "MM439"]
