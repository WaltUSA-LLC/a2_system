"""
Test cases for /base/shift/detail API:

1. Output schema
   - Verify the API returns machine-detail records with expected fields.

2. Extractor arguments
   - Verify extract_base_data receives MESExtractor, start as both start/end,
     and shift.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content.

4. Metric and comment serialization
   - Verify calculated metrics and comments are returned as JSON-safe values.

5. Duplicate machine rows
   - Verify duplicate MachID rows are preserved as detail records.

6. Shift_Start_Time formatting
   - Verify Shift_Start_Time is serialized as a string.

7. Zero ST_prs behavior
   - Verify infinite Mach_Efficiency is serialized as null.

8. NaN ST_prs behavior
   - Verify NaN Mach_Efficiency is serialized as null.
"""


from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app.services.shift_view as shift_view
from app.main import app
from app.tests.mocks.handle_shift_mach_detail_mocks import (
    make_base_shift_mach_detail_df,
    make_empty_shift_mach_detail_df,
    make_shift_mach_detail_df_for_metrics_and_comments,
    make_shift_mach_detail_df_with_duplicate_mach,
    make_shift_mach_detail_df_with_nan_st_prs,
    make_shift_mach_detail_df_with_zero_st_prs,
)
from extractors import MESExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Shift_Start_Time",
    "Style_Code",
    "Weight",
    "MES_prs",
    "NAU_prs",
    "ON_Time",
    "OFF_Time",
    "ON_Time_Occupation",
    "Mach_Efficiency",
    "Comment",
]


def _patch_extract_base_data(monkeypatch, df):
    extract_mock = Mock(
        side_effect=lambda extractor_cls, start_time, end_time, shift=0: df.copy()
    )
    monkeypatch.setattr(
        shift_view,
        "extract_base_data",
        extract_mock,
    )
    return extract_mock


def test_shift_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns machine-detail records with expected fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_shift_mach_detail_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 3
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_shift_detail_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify that the API path passes start as both start_time and end_time,
    plus shift, to extract_base_data through handle_shift_mach_detail.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_shift_mach_detail_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-01",
        1,
    )


def test_shift_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_shift_mach_detail_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_shift_detail_api_metrics_and_comments(monkeypatch):
    """
    Case 4: Metric and comment serialization.
    Metric calculations should be serialized through the API, and comments
    should reflect machine efficiency.
    """
    df = make_shift_mach_detail_df_for_metrics_and_comments()
    df.loc[df["MachID"] == "M_LOW", ["ON_Time", "OFF_Time", "Avg_Cycle", "Weight"]] = [
        90,
        10,
        10,
        1,
    ]

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    result_by_mach = {
        record["MachID"]: record
        for record in content
    }

    good = result_by_mach["M_GOOD"]
    low = result_by_mach["M_LOW"]

    assert good["MES_prs"] == 9
    assert good["ON_Time_Occupation"] == pytest.approx(0.9)
    assert good["Mach_Efficiency"] == pytest.approx(1.8)
    assert good["Comment"] == "Good"

    assert low["MES_prs"] == 1
    assert low["ON_Time_Occupation"] == pytest.approx(0.9)
    assert low["Mach_Efficiency"] == pytest.approx(0.2)
    assert low["Comment"] == "Low Ef"


def test_shift_detail_api_duplicate_mach_rows_preserved(monkeypatch):
    """
    Case 5: Duplicate machine rows.
    Duplicate MachID rows should remain separate detail records.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_shift_mach_detail_df_with_duplicate_mach(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    m1_records = [
        record
        for record in content
        if record["MachID"] == "M1"
    ]

    assert len(content) == 3
    assert len(m1_records) == 2


def test_shift_detail_api_shift_start_time_is_string(monkeypatch):
    """
    Case 6: Shift_Start_Time formatting.
    Shift_Start_Time should be converted from Timestamp to string before API
    serialization.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_shift_mach_detail_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    row = response.json()["content"][0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"


def test_shift_detail_api_zero_st_prs_current_behavior(monkeypatch):
    """
    Case 7: Zero ST_prs behavior.
    If ST_prs is 0 and MES_prs is positive, Mach_Efficiency becomes
    infinite and should be serialized as null.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_shift_mach_detail_df_with_zero_st_prs(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M_ZERO_ST"
    assert row["MES_prs"] == 5
    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == "Good"


def test_shift_detail_api_nan_st_prs_current_behavior(monkeypatch):
    """
    Case 8: NaN ST_prs behavior.
    If ST_prs is NaN, Mach_Efficiency should be serialized as null and the
    comment should remain empty.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_shift_mach_detail_df_with_nan_st_prs(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M1"
    assert row["MES_prs"] == 5
    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == ""
