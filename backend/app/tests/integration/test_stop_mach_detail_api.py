"""
Integration tests for /base/stop/mach/detail.

These tests keep detailed business-rule coverage in the corresponding unit
tests and focus on route wiring, extractor boundary, response shape, JSON
serialization, and request validation. Only extract_base_data is mocked.
"""

from unittest.mock import Mock

from fastapi.testclient import TestClient

import app.services.stop_view as stop_view
from app.main import app
from app.tests.mocks.handle_stop_mach_detail_mocks import (
    make_base_stop_mach_detail_df,
    make_empty_stop_mach_detail_df,
)
from extractors import StopExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "Stop_code",
    "Description",
    "MachID",
    "Style_Code",
    "Stop_time",
    "Recover_time",
    "duration",
    "Start_Shift_Time",
]


def _patch_extract_base_data(monkeypatch, df):
    extract_mock = Mock(
        side_effect=lambda extractor_cls, start_time, end_time, shift=0: df.copy()
    )
    monkeypatch.setattr(
        stop_view,
        "extract_base_data",
        extract_mock,
    )
    return extract_mock


def _get_stop_mach_detail(**overrides):
    params = {
        "start": "2026-05-01",
        "end": "2026-05-02",
        "shift": 0,
        "mach": 1,
        "style": "ABC",
    }
    params.update(overrides)

    return client.get(
        "/base/stop/mach/detail",
        params=params,
    )


def test_stop_mach_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns the expected top-level response and row fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_mach_detail_df(),
    )

    response = _get_stop_mach_detail()

    assert response.status_code == 200
    body = response.json()

    assert list(body.keys()) == ["content"]
    assert list(body["content"][0].keys()) == EXPECTED_COLUMNS


def test_stop_mach_detail_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify the API path passes start and end to extract_base_data through
    handle_stop_mach_detail. Current behavior does not pass shift, mach, or
    style.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_stop_mach_detail_df(),
    )

    response = _get_stop_mach_detail(shift=1, mach=1, style="ABC")

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        StopExtractor,
        "2026-05-01",
        "2026-05-02",
    )


def test_stop_mach_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_stop_mach_detail_df(),
    )

    response = _get_stop_mach_detail()

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_stop_mach_detail_api_detail_serialization(monkeypatch):
    """
    Case 4: Representative transformation and serialization.
    Verify filtered detail rows serialize strings, ints, and timedeltas.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_mach_detail_df(),
    )

    response = _get_stop_mach_detail(mach=1, style="ABC")

    assert response.status_code == 200
    content = response.json()["content"]
    result_by_stop_code = {
        record["Stop_code"]: record
        for record in content
    }

    assert len(content) == 2
    assert set(result_by_stop_code) == {10, 20}

    stop_10 = result_by_stop_code[10]
    stop_20 = result_by_stop_code[20]

    assert stop_10["Description"] == "Jam"
    assert stop_10["MachID"] == 1
    assert stop_10["Style_Code"] == "ABC"
    assert stop_10["Stop_time"] == "2026-05-01 08:00:00"
    assert stop_10["Recover_time"] == "2026-05-01 08:05:00"
    assert stop_10["duration"] == 300.0

    assert stop_20["Description"] == "Low Air"
    assert stop_20["duration"] == 900.0


def test_stop_mach_detail_api_requires_query_params():
    """
    Case 5: Required query validation.
    Missing required route parameters should be rejected by FastAPI before
    the handler runs.
    """
    required_params = ["start", "end", "shift", "mach", "style"]

    for missing_param in required_params:
        params = {
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 0,
            "mach": 1,
            "style": "ABC",
        }
        params.pop(missing_param)

        response = client.get(
            "/base/stop/mach/detail",
            params=params,
        )

        assert response.status_code == 422
