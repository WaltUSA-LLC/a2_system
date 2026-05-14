"""
Test cases for /base/stop/code API:

1. Output schema
   - Verify the API returns table and chart payloads with expected fields.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start, and end.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API payloads.

4. Metric serialization
   - Verify count metrics and Timedelta values are serialized correctly.
"""

from unittest.mock import Mock

from fastapi.testclient import TestClient

import app.services.stop_view as stop_view
from app.main import app
from app.tests.mocks.handle_stop_view_by_code_mocks import (
    make_base_stop_view_by_code_df,
    make_empty_stop_view_by_code_df,
)
from extractors import StopExtractor


client = TestClient(app)


EXPECTED_TABLE_COLUMNS = [
    "id",
    "Stop_code",
    "Description",
    "Mach_cnt",
    "freq",
    "dur_sum",
    "dur_med",
]
EXPECTED_FREQ_CHART_COLUMNS = ["Stop_code", "Description", "freq"]
EXPECTED_MACH_CHART_COLUMNS = ["Stop_code", "Description", "Mach_cnt"]
EXPECTED_DUR_SUM_CHART_COLUMNS = ["Stop_code", "Description", "dur_sum"]
EXPECTED_DUR_MED_CHART_COLUMNS = ["Stop_code", "Description", "dur_med"]


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


def _get_stop_code(shift=0):
    return client.get(
        "/base/stop/code",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": shift,
        },
    )


def test_stop_code_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns table and chart payloads with expected fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_view_by_code_df(),
    )

    response = _get_stop_code()

    assert response.status_code == 200
    body = response.json()

    assert list(body.keys()) == [
        "content",
        "chart_freq",
        "chart_mach",
        "chart_dur_sum",
        "chart_dur_med",
    ]
    assert list(body["content"][0].keys()) == EXPECTED_TABLE_COLUMNS
    assert list(body["chart_freq"][0].keys()) == EXPECTED_FREQ_CHART_COLUMNS
    assert list(body["chart_mach"][0].keys()) == EXPECTED_MACH_CHART_COLUMNS
    assert list(body["chart_dur_sum"][0].keys()) == EXPECTED_DUR_SUM_CHART_COLUMNS
    assert list(body["chart_dur_med"][0].keys()) == EXPECTED_DUR_MED_CHART_COLUMNS


def test_stop_code_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify that the API path passes start and end to extract_base_data
    through handle_stop_view_by_code. Current behavior does not pass shift.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_stop_view_by_code_df(),
    )

    response = _get_stop_code(shift=1)

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        StopExtractor,
        "2026-05-01",
        "2026-05-02",
    )


def test_stop_code_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty arrays for the table and all charts.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_stop_view_by_code_df(),
    )

    response = _get_stop_code()

    assert response.status_code == 200
    assert response.json() == {
        "content": [],
        "chart_freq": [],
        "chart_mach": [],
        "chart_dur_sum": [],
        "chart_dur_med": [],
    }


def test_stop_code_api_metric_serialization(monkeypatch):
    """
    Case 4: Metric serialization.
    Count metrics and Timedelta values should serialize correctly in table
    and chart payloads.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_stop_view_by_code_df(),
    )

    response = _get_stop_code()

    assert response.status_code == 200
    body = response.json()
    content = body["content"]
    result_by_code = {
        record["Stop_code"]: record
        for record in content
    }

    jam = result_by_code[10]
    low = result_by_code[20]

    assert jam["Mach_cnt"] == 2
    assert jam["freq"] == 2
    assert jam["dur_sum"] == 1800.0
    assert jam["dur_med"] == 900.0

    assert low["Mach_cnt"] == 1
    assert low["freq"] == 1
    assert low["dur_sum"] == 300.0
    assert low["dur_med"] == 300.0

    
