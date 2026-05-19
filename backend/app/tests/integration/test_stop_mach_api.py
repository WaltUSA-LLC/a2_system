"""
Integration tests for /base/stop/mach.

These tests keep detailed business-rule coverage in the corresponding unit
tests and focus on route wiring, extractor boundary, response shape, JSON
serialization, and request validation. Only extract_base_data is mocked.
"""
from fastapi.testclient import TestClient

import app.services.stop_view as stop_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.handle_stop_view_by_mach_mocks import (
    make_base_stop_view_by_mach_df,
    make_empty_stop_view_by_mach_df,
)
from extractors import StopExtractor


client = TestClient(app)


EXPECTED_TABLE_COLUMNS = ["id", "MachID", "Style_Code", "freq"]
EXPECTED_CHART_COLUMNS = ["MachID", "freq"]


def _get_stop_mach(**overrides):
    params = {
        "start": "2026-05-01",
        "end": "2026-05-02",
        "shift": 0,
    }
    params.update(overrides)

    return client.get(
        "/base/stop/mach",
        params=params,
    )


def test_stop_mach_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns the expected top-level response and row fields.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_mach_df(),
    )

    response = _get_stop_mach()

    assert response.status_code == 200
    body = response.json()

    assert list(body.keys()) == ["content", "chart"]
    assert list(body["content"][0].keys()) == EXPECTED_TABLE_COLUMNS
    assert list(body["chart"][0].keys()) == EXPECTED_CHART_COLUMNS


def test_stop_mach_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify the API path passes start and end to extract_base_data through
    handle_stop_view_by_mach. Current behavior does not pass shift.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_mach_df(),
    )

    response = _get_stop_mach(shift=1)

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        StopExtractor,
        "2026-05-01",
        "2026-05-02",
    )


def test_stop_mach_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty arrays for the table and chart.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_view_by_mach_df(),
    )

    response = _get_stop_mach()

    assert response.status_code == 200
    assert response.json() == {"content": [], "chart": []}


def test_stop_mach_api_frequency_serialization(monkeypatch):
    """
    Case 4: Representative transformation and serialization.
    Machine/style and machine-only frequency counts should serialize as ints.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_mach_df(),
    )

    response = _get_stop_mach()

    assert response.status_code == 200
    body = response.json()
    content_by_mach_style = {
        (record["MachID"], record["Style_Code"]): record
        for record in body["content"]
    }
    chart_by_mach = {
        record["MachID"]: record
        for record in body["chart"]
    }

    assert content_by_mach_style[("M1", "ABC")]["freq"] == 2
    assert content_by_mach_style[("M2", "XYZ")]["freq"] == 1
    assert chart_by_mach["M1"]["freq"] == 2
    assert chart_by_mach["M2"]["freq"] == 1


def test_stop_mach_api_requires_query_params():
    """
    Case 5: Required query validation.
    Missing required route parameters should be rejected by FastAPI before
    the handler runs.
    """
    required_params = ["start", "end", "shift"]

    for missing_param in required_params:
        params = {
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 0,
        }
        params.pop(missing_param)

        response = client.get(
            "/base/stop/mach",
            params=params,
        )

        assert response.status_code == 422
