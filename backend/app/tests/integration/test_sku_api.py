"""
Test cases for /base/sku API:

1. Output schema
   - Verify the API returns SKU records with expected fields.

2. Extractor arguments
   - Verify extract_base_data receives MESExtractor, start, end, and shift.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content.

4. Single SKU aggregation
   - Verify one Style_Code and Shift_Start_Time group is aggregated and serialized.

5. Multiple SKU and multiple shift aggregation
   - Verify multiple Style_Code and Shift_Start_Time groups produce records.

6. Invalid Style_Code handling
   - Verify empty or null style codes are dropped by grouping.

7. Null Efficiency serialization
   - Verify NaN or infinite efficiency values are serialized as null.

8. Null ON_Time_Occupation serialization
   - Verify zero denominator values are serialized as null.

9. NaN ON/OFF time serialization
   - Verify NaN ON/OFF values are serialized as null.
"""


from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app.services.sku_view as sku_view
from app.main import app
from app.tests.mocks.handle_sku_view_mocks import (
    make_base_sku_df,
    make_empty_sku_df,
    make_multi_sku_multi_shift_df,
    make_sku_df_with_invalid_style_code,
    make_sku_df_with_nan_st_prs,
    make_sku_df_with_zero_st_prs,
    make_sku_df_with_zero_on_off_time,
    make_sku_df_with_nan_on_time,
)
from extractors import MESExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "Style_Code",
    "Shift_Start_Time",
    "Mach_cnt",
    "NAU_prs",
    "MES_prs",
    "ON_Time_Occupation",
    "Efficiency",
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


def test_sku_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns SKU records with expected fields.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_df(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_sku_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify that the API path passes request query parameters to
    extract_base_data through handle_sku_view.
    """
    extract_mock = _patch_extract_base_data(
        monkeypatch,
        make_base_sku_df(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_sku_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_empty_sku_df(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_sku_api_single_sku_aggregation(monkeypatch):
    """
    Case 4: Single SKU aggregation.
    Rows with the same normalized Style_Code and Shift_Start_Time should be
    grouped and serialized through the API.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_base_sku_df(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["id"] == 0
    assert row["Style_Code"] == "ABC"
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 8
    assert row["MES_prs"] == 7
    assert row["ON_Time_Occupation"] == pytest.approx(0.85)
    assert row["Efficiency"] == pytest.approx(0.7)


def test_sku_api_multiple_sku_multiple_shift_aggregation(monkeypatch):
    """
    Case 5: Multiple SKU and multiple shift aggregation.
    Multiple Style_Code and Shift_Start_Time groups should produce multiple
    API records.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_multi_sku_multi_shift_df(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 3

    result_by_style_shift = {
        (record["Style_Code"], record["Shift_Start_Time"]): record
        for record in content
    }

    abc_shift_1 = result_by_style_shift[("ABC", "2026-05-01 08:00:00")]
    xyz_shift_1 = result_by_style_shift[("XYZ", "2026-05-01 08:00:00")]
    abc_shift_2 = result_by_style_shift[("ABC", "2026-05-01 20:00:00")]

    assert abc_shift_1["Mach_cnt"] == 2
    assert abc_shift_1["NAU_prs"] == 6
    assert abc_shift_1["MES_prs"] == 8
    assert abc_shift_1["ON_Time_Occupation"] == pytest.approx(160 / 180)
    assert abc_shift_1["Efficiency"] == pytest.approx(8 / 9)

    assert xyz_shift_1["Mach_cnt"] == 1
    assert xyz_shift_1["NAU_prs"] == 7
    assert xyz_shift_1["MES_prs"] == 4
    assert xyz_shift_1["ON_Time_Occupation"] == pytest.approx(80 / 100)
    assert xyz_shift_1["Efficiency"] == pytest.approx(4 / 5)

    assert abc_shift_2["Mach_cnt"] == 1
    assert abc_shift_2["NAU_prs"] == 3
    assert abc_shift_2["MES_prs"] == 6
    assert abc_shift_2["ON_Time_Occupation"] == pytest.approx(90 / 100)
    assert abc_shift_2["Efficiency"] == pytest.approx(6 / 5)


def test_sku_api_invalid_style_code_is_dropped(monkeypatch):
    """
    Case 6: Invalid Style_Code handling.
    Empty or null style codes should be normalized to None and dropped by
    pandas groupby.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_df_with_invalid_style_code(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}


def test_sku_api_nan_efficiency_serializes_as_null(monkeypatch):
    """
    Case 7a: Null Efficiency serialization.
    If any row in a group has NaN ST_prs, group efficiency should serialize
    as null.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_df_with_nan_st_prs(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["Style_Code"] == "XYZ"
    assert row["MES_prs"] == 8
    assert row["Efficiency"] is None


def test_sku_api_infinite_efficiency_serializes_as_null(monkeypatch):
    """
    Case 7b: Null Efficiency serialization.
    If ST_prs is 0 and MES_prs is positive, infinite efficiency should
    serialize as null.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_df_with_zero_st_prs(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["Style_Code"] == "AAA"
    assert row["MES_prs"] == 10
    assert row["Efficiency"] is None


def test_sku_api_zero_on_off_time_occupation_serializes_as_null(monkeypatch):
    """
    Case 8: Null ON_Time_Occupation serialization.
    If grouped ON_Time + OFF_Time is 0, ON_Time_Occupation becomes NaN and
    should serialize as null.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_df_with_zero_on_off_time(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["Style_Code"] == "ZERO"
    assert row["MES_prs"] == 10
    assert row["ON_Time_Occupation"] is None
    assert row["Efficiency"] is None


def test_sku_api_nan_on_off_time_serializes_as_null(monkeypatch):
    """
    Case 9: NaN ON/OFF time serialization.
    If grouped ON_Time + OFF_Time is NaN, ON_Time_Occupation and Efficiency
    should serialize as null.
    """
    _patch_extract_base_data(
        monkeypatch,
        make_sku_df_with_nan_on_time(),
    )

    response = client.get(
        "/base/sku",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["Style_Code"] == "NAN"
    assert row["MES_prs"] == 10
    assert row["ON_Time_Occupation"] is None
    assert row["Efficiency"] is None
