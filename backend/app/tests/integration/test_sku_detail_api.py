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
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

import app.services.sku_view as sku_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
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


def test_sku_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns SKU machine-detail records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    extract_mock = patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
    patch_extract_base_data(
        monkeypatch,
        sku_view,
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

    patch_extract_base_data(
        monkeypatch,
        sku_view,
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
