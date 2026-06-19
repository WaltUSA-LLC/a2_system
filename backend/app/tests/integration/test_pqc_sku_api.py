"""
Test cases for /base/pqc/sku API:

1. Output schema
   - Verify the API returns SKU-level PQC records with expected fields.

2. Empty extractor result
   - Verify an empty raw PQC DataFrame returns empty API content.
   - Verify extract_base_data receives PQCExtractor, start, end, and shift.

3. SKU aggregation and serialization
   - Verify raw extractor rows are normalized, grouped by SKU, and returned
     as JSON-safe values.

4. Multiple shift sorting
   - Verify multiple shifts are serialized with formatted shift start times.
"""

import pytest
from fastapi.testclient import TestClient

import app.services.pqc_view as pqc_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.extract_pqc_data_input_mocks import (
    make_base_raw_pqc_df,
    make_empty_raw_pqc_df,
    make_multi_shift_raw_pqc_df,
)


client = TestClient(app)


DEFECT_COLUMNS = [
    "toeHole",
    "brokenNDL",
    "missNDL",
    "fanYarn",
    "missYarn",
    "logoIssue",
    "dirty",
    "feisha",
    "other",
]

EXPECTED_COLUMNS = [
    "id",
    "Shift_Start_Time",
    "Style_Code",
    "pqc_cnt",
    *DEFECT_COLUMNS,
    "defects",
]


def _get_pqc_sku(start="2026-05-01", end="2026-05-02", shift=1):
    return client.get(
        "/base/pqc/sku",
        params={
            "start": start,
            "end": end,
            "shift": shift,
        },
    )


def _content_by_style(content):
    return {
        record["Style_Code"]: record
        for record in content
    }


def _content_by_style_shift(content):
    return {
        (record["Style_Code"], record["Shift_Start_Time"]): record
        for record in content
    }


def test_pqc_sku_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns content records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_sku()

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_pqc_sku_api_empty_df(monkeypatch):
    """
    Case 2: Empty extractor result.
    If the extractor returns an empty raw PQC DataFrame, the API should return
    empty content while still passing request parameters to extract_base_data.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_empty_raw_pqc_df(),
    )

    response = _get_pqc_sku(
        start="2026-05-03",
        end="2026-05-04",
        shift=2,
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-03",
        "2026-05-04",
        2,
    )


def test_pqc_sku_api_sku_aggregation_and_serialization(monkeypatch):
    """
    Case 3: SKU aggregation and serialization.
    Raw extractor rows should be normalized, grouped, and serialized through
    the API.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_sku()

    assert response.status_code == 200
    content = response.json()["content"]
    result_by_style = _content_by_style(content)

    assert set(result_by_style) == {"ABC BLUE", "ABC RED"}

    abc_red = result_by_style["ABC RED"]
    assert abc_red["id"] == 1
    assert abc_red["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert abc_red["pqc_cnt"] == 2
    assert abc_red["toeHole"] == 2
    assert abc_red["brokenNDL"] == 0
    assert abc_red["missNDL"] == 1
    assert abc_red["missYarn"] == 0
    assert abc_red["defects"] == 3

    abc_blue = result_by_style["ABC BLUE"]
    assert abc_blue["id"] == 0
    assert abc_blue["pqc_cnt"] == 1
    assert abc_blue["brokenNDL"] == 1
    assert abc_blue["missYarn"] == 1
    assert abc_blue["defects"] == 2


def test_pqc_sku_api_multiple_shift_sorting(monkeypatch):
    """
    Case 4: Multiple shift sorting.
    Multiple shift start times should be sorted and returned as formatted
    strings.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_multi_shift_raw_pqc_df(),
    )

    response = _get_pqc_sku(shift=0)

    assert response.status_code == 200
    content = response.json()["content"]
    shift_values = [
        record["Shift_Start_Time"]
        for record in content
    ]
    result_by_style_shift = _content_by_style_shift(content)

    assert shift_values == sorted(shift_values)
    assert set(shift_values) == {
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
        "2026-05-02 07:00:00",
    }
    assert result_by_style_shift[
        ("ABC RED", "2026-05-01 07:00:00")
    ]["defects"] == 2
    assert result_by_style_shift[
        ("XYZ BLACK", "2026-05-01 19:00:00")
    ]["defects"] == 4
    assert result_by_style_shift[
        ("QWE WHITE", "2026-05-02 07:00:00")
    ]["defects"] == 3
