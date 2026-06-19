"""
Test cases for /base/pqc/staff/detail API:

1. Output schema
   - Verify the API returns staff-detail PQC records with expected fields.

2. Empty extractor result
   - Verify an empty raw PQC DataFrame returns empty API content.
   - Verify extract_base_data receives PQCExtractor, start as both start/end,
     and shift.

3. Name filtering and sorting
   - Verify raw rows are normalized, filtered by exact staff name, sorted by
     DateRec, and serialized through the API.

4. Style code normalization
   - Verify raw style codes are stripped and upper-cased before serialization.

5. JSON-safe value cleanup
   - Verify NaN and infinity values are returned as JSON null.
"""

from fastapi.testclient import TestClient

import app.services.pqc_view as pqc_view
from app.main import app
from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.extract_pqc_data_input_mocks import (
    make_base_raw_pqc_df,
    make_empty_raw_pqc_df,
    make_raw_pqc_staff_detail_df_with_invalid_values,
)


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "DateRec",
    "MachID",
    "Style_Code",
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


def _get_pqc_staff_detail(start="2026-05-01", shift=1, name="Alice"):
    return client.get(
        "/base/pqc/staff/detail",
        params={
            "start": start,
            "shift": shift,
            "name": name,
        },
    )


def _content_by_mach(content):
    return {
        record["MachID"]: record
        for record in content
    }


def test_pqc_staff_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns content records with expected fields.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_staff_detail()

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_pqc_staff_detail_api_empty_df(monkeypatch):
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

    response = _get_pqc_staff_detail(
        start="2026-05-03",
        shift=2,
        name="Alice",
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-03",
        "2026-05-03",
        2,
    )


def test_pqc_staff_detail_api_name_filtering_and_sorting(monkeypatch):
    """
    Case 3: Name filtering and sorting.
    Only exact-name matches should be returned, sorted by DateRec, with
    DateRec formatted as strings.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_staff_detail(name="Alice")

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert [record["DateRec"] for record in content] == [
        "2026-05-01 07:10:00",
        "2026-05-01 07:35:00",
    ]
    assert [record["id"] for record in content] == [0, 2]
    assert [record["MachID"] for record in content] == ["M1", "M1"]


def test_pqc_staff_detail_api_style_code_normalization(monkeypatch):
    """
    Case 4: Style code normalization.
    Raw style code whitespace and casing should be normalized before the API
    returns detail rows.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    response = _get_pqc_staff_detail(name="Alice")

    assert response.status_code == 200
    assert [
        record["Style_Code"]
        for record in response.json()["content"]
    ] == ["ABC RED", "ABC RED"]


def test_pqc_staff_detail_api_replaces_invalid_values(monkeypatch):
    """
    Case 5: JSON-safe value cleanup.
    NaN, positive infinity, and negative infinity values should become JSON
    null in the API response.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_raw_pqc_staff_detail_df_with_invalid_values(),
    )

    response = _get_pqc_staff_detail(name="Alice")

    assert response.status_code == 200
    content = response.json()["content"]
    row_by_mach = _content_by_mach(content)

    assert [record["MachID"] for record in content] == ["M2", "M1"]
    assert [record["Style_Code"] for record in content] == [
        "XYZ BLACK",
        "ABC RED",
    ]
    assert row_by_mach["M1"]["brokenNDL"] is None
    assert row_by_mach["M1"]["dirty"] is None
    assert row_by_mach["M2"]["missNDL"] is None
