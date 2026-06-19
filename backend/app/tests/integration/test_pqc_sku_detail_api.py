"""
Test cases for /base/pqc/sku/detail API:

1. Output schema
   - Verify the API returns machine-level PQC records with expected fields.

2. Empty extractor result
   - Verify an empty raw PQC DataFrame returns empty API content.
   - Verify extract_base_data receives PQCExtractor, start as both start/end,
     and shift.

3. Style filtering and machine aggregation
   - Verify raw extractor rows are normalized, filtered by style, grouped by
     machine, and returned through the API.
"""

from fastapi.testclient import TestClient

import app.services.pqc_view as pqc_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.extract_pqc_data_input_mocks import (
    make_base_raw_pqc_df,
    make_empty_raw_pqc_df,
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
    "MachID",
    "pqc_cnt",
    *DEFECT_COLUMNS,
    "defects",
]


def _get_pqc_sku_detail(start="2026-05-01", shift=1, style="ABC RED"):
    return client.get(
        "/base/pqc/sku/detail",
        params={
            "start": start,
            "shift": shift,
            "style": style,
        },
    )


def test_pqc_sku_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns content records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_sku_detail()

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_pqc_sku_detail_api_empty_df(monkeypatch):
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

    response = _get_pqc_sku_detail(
        start="2026-05-03",
        shift=2,
        style="ABC RED",
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-03",
        "2026-05-03",
        2,
    )


def test_pqc_sku_detail_api_style_filtering_and_machine_aggregation(
    monkeypatch,
):
    """
    Case 3: Style filtering and machine aggregation.
    Raw extractor rows should be normalized, filtered by exact Style_Code, and
    grouped by machine through the API.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_sku_detail(style="ABC RED")

    assert response.status_code == 200
    content = response.json()["content"]

    assert content == [
        {
            "id": 0,
            "Shift_Start_Time": "2026-05-01 07:00:00",
            "MachID": "M1",
            "pqc_cnt": 2,
            "toeHole": 2,
            "brokenNDL": 0,
            "missNDL": 1,
            "fanYarn": 0,
            "missYarn": 0,
            "logoIssue": 0,
            "dirty": 0,
            "feisha": 0,
            "other": 0,
            "defects": 3,
        }
    ]
