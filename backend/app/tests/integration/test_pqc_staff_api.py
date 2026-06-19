"""
Test cases for /base/pqc/staff API:

1. Output schema
   - Verify the API returns staff-level PQC records with expected fields.

2. Empty extractor result
   - Verify an empty raw PQC DataFrame returns empty API content.

3. Staff aggregation and serialization
   - Verify raw extractor rows are normalized, grouped by staff, and returned
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
    "Name",
    "Role",
    "pqc_cnt",
    "start_check",
    "end_check",
    "avg_adj_diff",
    *DEFECT_COLUMNS,
    "defects",
]


def _get_pqc_staff(start="2026-05-01", end="2026-05-02", shift=1):
    return client.get(
        "/base/pqc/staff",
        params={
            "start": start,
            "end": end,
            "shift": shift,
        },
    )


def _content_by_staff(content):
    return {
        (record["Name"], record["Role"]): record
        for record in content
    }


def _content_by_staff_shift(content):
    return {
        (record["Name"], record["Role"], record["Shift_Start_Time"]): record
        for record in content
    }


def test_pqc_staff_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns content records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_staff()

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_pqc_staff_api_empty_df(monkeypatch):
    """
    Case 2: Empty extractor result.
    If the extractor returns an empty raw PQC DataFrame, the API should
    return empty content.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_empty_raw_pqc_df(),
    )

    response = _get_pqc_staff()

    assert response.status_code == 200
    assert response.json() == {"content": []}
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_pqc_staff_api_staff_aggregation_and_serialization(monkeypatch):
    """
    Case 3: Staff aggregation and serialization.
    Raw extractor rows should be normalized, grouped, and serialized through
    the API with JSON-safe values.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_staff()

    assert response.status_code == 200
    content = response.json()["content"]
    result_by_staff = _content_by_staff(content)

    alice_ko = result_by_staff[("Alice", "KO")]
    assert alice_ko["id"] == 0
    assert alice_ko["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert alice_ko["pqc_cnt"] == 2
    assert alice_ko["start_check"] == "07:10:00"
    assert alice_ko["end_check"] == "07:35:00"
    assert alice_ko["avg_adj_diff"] == pytest.approx(1500.0)
    assert alice_ko["toeHole"] == 2
    assert alice_ko["brokenNDL"] == 0
    assert alice_ko["missNDL"] == 1
    assert alice_ko["missYarn"] == 0
    assert alice_ko["defects"] == 3

    bob_tech = result_by_staff[("Bob", "Tech")]
    assert bob_tech["id"] == 1
    assert bob_tech["pqc_cnt"] == 1
    assert bob_tech["start_check"] == "07:20:00"
    assert bob_tech["end_check"] == "07:20:00"
    assert bob_tech["avg_adj_diff"] is None
    assert bob_tech["brokenNDL"] == 1
    assert bob_tech["missYarn"] == 1
    assert bob_tech["defects"] == 2


def test_pqc_staff_api_multiple_shift_sorting(monkeypatch):
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

    response = _get_pqc_staff(shift=0)

    assert response.status_code == 200
    content = response.json()["content"]
    shift_values = [
        record["Shift_Start_Time"]
        for record in content
    ]
    result_by_staff_shift = _content_by_staff_shift(content)

    assert shift_values == sorted(shift_values)
    assert set(shift_values) == {
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
        "2026-05-02 07:00:00",
    }
    assert result_by_staff_shift[
        ("Alice", "KO", "2026-05-01 07:00:00")
    ]["defects"] == 2
    assert result_by_staff_shift[
        ("Cara", "KO", "2026-05-01 19:00:00")
    ]["defects"] == 4
    assert result_by_staff_shift[
        ("Dan", "Tech", "2026-05-02 07:00:00")
    ]["defects"] == 3
