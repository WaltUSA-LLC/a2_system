"""
Test cases for /base/sku/detail API:

1. Output schema
   - Verify the API returns SKU machine-detail records with expected fields.

2. Extractor arguments
   - Verify extract_base_data receives MESExtractor, start, end, and shift.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content.

4. Style filtering
   - Verify style filtering uses Style_Code without size/color suffix.

5. No matching style
   - Verify no matching style returns empty API content.

6. Metric and comment serialization
   - Verify calculated metrics and comments are returned as JSON-safe values.

7. Machine sorting
   - Verify returned records are sorted by MachID.

8. Shift_Start_Time formatting
   - Verify Shift_Start_Time is serialized as a string.

9. Invalid Style_Code handling
   - Verify empty or null style codes are excluded without error.

10. Style argument case sensitivity
    - Verify lowercase style argument does not match uppercase normalized rows.

11. NaN ST_prs behavior
    - Verify NaN Mach_Efficiency is serialized as null.

12. Zero ST_prs behavior
    - Verify infinite Mach_Efficiency is serialized as null.

13. NaN ON/OFF time behavior
    - Verify NaN ON_Time + OFF_Time serializes dependent metrics as null.

14. Zero ON/OFF time behavior
    - Verify zero ON_Time + OFF_Time serializes dependent metrics as null.
"""


from unittest.mock import Mock

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.services.sku_view as sku_view
from app.main import app
from app.tests.mocks.handle_sku_mach_detail_mocks import (
    make_base_sku_mach_detail_df,
    make_empty_sku_mach_detail_df,
    make_sku_mach_detail_df_for_metrics_and_comments,
    make_sku_mach_detail_df_with_invalid_style_code,
    make_sku_mach_detail_df_without_matching_style,
    make_unsorted_sku_mach_detail_df,
)
from extractors import MESExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Shift_Start_Time",
    "Style_Code",
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
        sku_view,
        "extract_base_data",
        extract_mock,
    )
    return extract_mock


def test_sku_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns SKU machine-detail records with expected fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_sku_detail_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify that the API path passes request query parameters to
    extract_base_data through handle_sku_mach_detail.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_sku_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_sku_detail_api_filters_by_style_without_size(monkeypatch):
    """
    Case 4: Style filtering.
    Style filtering should use the first token of Style_Code after stripping
    and uppercasing, while final Style_Code keeps the full cleaned value.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert {row["Style_Code"] for row in content} == {"ABC RED", "ABC BLUE"}
    assert "XYZ BLACK" not in {row["Style_Code"] for row in content}


def test_sku_detail_api_no_matching_style_returns_empty(monkeypatch):
    """
    Case 5: No matching style.
    If no row matches style, the API should return empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_mach_detail_df_without_matching_style(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_sku_detail_api_metrics_and_comments(monkeypatch):
    """
    Case 6: Metric and comment serialization.
    Metric calculations should be serialized through the API, and comments
    should reflect machine efficiency.
    """
    df = make_sku_mach_detail_df_for_metrics_and_comments()
    df.loc[df["MachID"] == "M2", "Weight"] = 1
    df.loc[df["MachID"] == "M3", ["ON_Time", "OFF_Time", "Avg_Cycle"]] = [
        4,
        2,
        1,
    ]

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    result_by_mach = {
        record["MachID"]: record
        for record in content
    }

    good = result_by_mach["M1"]
    low = result_by_mach["M2"]
    rounded_low = result_by_mach["M3"]

    assert good["MES_prs"] == 8
    assert good["ON_Time_Occupation"] == pytest.approx(0.8)
    assert good["Mach_Efficiency"] == pytest.approx(1.6)
    assert good["Comment"] == "Good"

    assert low["MES_prs"] == 1
    assert low["ON_Time_Occupation"] == pytest.approx(0.5)
    assert low["Mach_Efficiency"] == pytest.approx(0.2)
    assert low["Comment"] == "Low Ef"

    assert rounded_low["MES_prs"] == 1
    assert rounded_low["ON_Time_Occupation"] == pytest.approx(0.667)
    assert rounded_low["Mach_Efficiency"] == pytest.approx(0.333)
    assert rounded_low["Comment"] == "Low Ef"


def test_sku_detail_api_sorts_by_mach_id(monkeypatch):
    """
    Case 7: Machine sorting.
    Output rows should be sorted by MachID ascending.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_unsorted_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert [record["MachID"] for record in content] == ["M1", "M2", "M3"]


def test_sku_detail_api_shift_start_time_is_string(monkeypatch):
    """
    Case 8: Shift_Start_Time formatting.
    Shift_Start_Time should be converted from Timestamp to string before API
    serialization.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    row = response.json()["content"][0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"


def test_sku_detail_api_invalid_style_code_is_excluded(monkeypatch):
    """
    Case 9: Invalid Style_Code handling.
    Style_Code values like "" and None should become None after cleaning,
    so they should not match the requested style.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_mach_detail_df_with_invalid_style_code(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M3"
    assert row["Style_Code"] == "ABC RED"


def test_sku_detail_api_style_argument_is_case_sensitive(monkeypatch):
    """
    Case 10: Style argument case sensitivity.
    Current behavior: Style_Code is normalized to uppercase, but style
    argument is not. A lowercase style argument should not match.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_mach_detail_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "abc",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_sku_detail_api_nan_st_prs_serializes_as_null(monkeypatch):
    """
    Case 11: NaN ST_prs behavior.
    If ST_prs is NaN, Mach_Efficiency should be serialized as null and the
    comment should remain empty.
    """
    df = make_base_sku_mach_detail_df()
    df = df[df["MachID"] == "M1"].copy()
    df["Avg_Cycle"] = df["Avg_Cycle"].astype(float)
    df.loc[:, "Avg_Cycle"] = np.nan

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
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


def test_sku_detail_api_zero_st_prs_serializes_as_null(monkeypatch):
    """
    Case 12: Zero ST_prs behavior.
    If ST_prs is 0 and MES_prs is positive, Mach_Efficiency becomes
    infinite and should be serialized as null.
    """
    df = make_base_sku_mach_detail_df()
    df = df[df["MachID"] == "M1"].copy()
    df.loc[:, ["ON_Time", "OFF_Time", "Avg_Cycle", "Weight"]] = [
        1,
        1,
        10,
        5,
    ]

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M1"
    assert row["MES_prs"] == 5
    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == "Good"


def test_sku_detail_api_nan_on_off_time_sum_serializes_as_null(monkeypatch):
    """
    Case 13: NaN ON/OFF time behavior.
    If ON_Time + OFF_Time is NaN, ON_Time_Occupation and Mach_Efficiency
    should be serialized as null and the comment should remain empty.
    """
    df = make_base_sku_mach_detail_df()
    df = df[df["MachID"] == "M1"].copy()
    df["ON_Time"] = df["ON_Time"].astype(float)
    df.loc[:, "ON_Time"] = np.nan

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M1"
    assert row["ON_Time"] is None
    assert row["OFF_Time"] == 40
    assert row["MES_prs"] == 5
    assert row["ON_Time_Occupation"] is None
    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == ""


def test_sku_detail_api_zero_on_off_time_sum_serializes_as_null(monkeypatch):
    """
    Case 14: Zero ON/OFF time behavior.
    If ON_Time + OFF_Time is 0, ON_Time_Occupation becomes NaN and
    Mach_Efficiency becomes infinite. Both should serialize as null.
    """
    df = make_base_sku_mach_detail_df()
    df = df[df["MachID"] == "M1"].copy()
    df.loc[:, ["ON_Time", "OFF_Time", "Avg_Cycle", "Weight"]] = [
        0,
        0,
        10,
        5,
    ]

    _patch_extract_base_data(
        monkeypatch,
        df,
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["MachID"] == "M1"
    assert row["ON_Time"] == 0
    assert row["OFF_Time"] == 0
    assert row["MES_prs"] == 5
    assert row["ON_Time_Occupation"] is None
    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == "Good"
