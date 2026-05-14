"""
Integration tests for /base/stop/code/detail.

These tests keep handler business-rule coverage in the corresponding unit
tests and focus on route wiring, extractor boundary, response shape, JSON
serialization, and request validation.
"""

from unittest.mock import Mock

from fastapi.testclient import TestClient

import app.services.stop_view as stop_view
from app.main import app
from app.tests.mocks.handle_stop_code_detail_mocks import (
    make_base_stop_code_detail_df,
    make_empty_stop_code_detail_df,
)
from extractors import StopExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Style_Code",
    "freq",
    "dur_sum",
    "dur_med",
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


def _get_stop_code_detail(**overrides):
    params = {
        "start": "2026-05-01",
        "end": "2026-05-02",
        "shift": 0,
        "stop_code": 10,
    }
    params.update(overrides)

    return client.get(
        "/base/stop/code/detail",
        params=params,
    )


def test_stop_code_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns the expected top-level response and row fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_code_detail_df(),
    )

    response = _get_stop_code_detail()

    assert response.status_code == 200
    body = response.json()

    assert list(body.keys()) == ["content"]
    assert list(body["content"][0].keys()) == EXPECTED_COLUMNS


def test_stop_code_detail_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify the API path passes start and end to extract_base_data through
    handle_stop_code_detail. Current behavior does not pass shift or stop_code.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_stop_code_detail_df(),
    )

    response = _get_stop_code_detail(shift=1, stop_code=10)

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        StopExtractor,
        "2026-05-01",
        "2026-05-02",
    )


def test_stop_code_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_stop_code_detail_df(),
    )

    response = _get_stop_code_detail()

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_stop_code_detail_api_metric_serialization(monkeypatch):
    """
    Case 4: Representative transformation and serialization.
    Timedelta metrics should serialize as seconds while counts remain ints.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_code_detail_df(),
    )

    response = _get_stop_code_detail(stop_code=10)

    assert response.status_code == 200
    content = response.json()["content"]
    result_by_mach_style = {
        (record["MachID"], record["Style_Code"]): record
        for record in content
    }

    mach_1_abc = result_by_mach_style[(1, "ABC")]
    mach_2_abc = result_by_mach_style[(2, "ABC")]

    assert len(content) == 2
    assert mach_1_abc["freq"] == 2
    assert mach_1_abc["dur_sum"] == 1200.0
    assert mach_1_abc["dur_med"] == 600.0

    assert mach_2_abc["freq"] == 1
    assert mach_2_abc["dur_sum"] == 1800.0
    assert mach_2_abc["dur_med"] == 1800.0


def test_stop_code_detail_api_requires_query_params():
    """
    Case 5: Required query validation.
    Missing required route parameters should be rejected by FastAPI before
    the handler runs.
    """
    required_params = ["start", "end", "shift", "stop_code"]

    for missing_param in required_params:
        params = {
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 0,
            "stop_code": 10,
        }
        params.pop(missing_param)

        response = client.get(
            "/base/stop/code/detail",
            params=params,
        )

        assert response.status_code == 422
