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
"""

import pytest
from fastapi.testclient import TestClient

import app.services.sku_view as sku_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.handle_sku_view_mocks import (
    make_base_sku_df,
    make_empty_sku_df,
    make_multi_sku_multi_shift_df,
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


def test_sku_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns SKU records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    extract_mock = patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
