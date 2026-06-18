"""
Test cases for handle_pqc_view_by_staff_detail:

1. Extractor arguments
   - Verify _extract_pqc_data receives start as both start and end, plus shift.

2. Output schema
   - Verify the returned DataFrame has the expected columns.

3. Name filtering
   - Verify only rows matching the requested Name are returned.

4. DateRec sorting and formatting
   - Verify DateRec is sorted ascending and returned as a string.

5. Style_Code cleanup
   - Verify Style_Code values are stripped.

6. JSON-safe value cleanup
   - Verify NaN and infinity values are replaced with None.

7. No matching name
   - Verify no matching Name returns an empty result schema.
"""

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_staff_df,
    make_pqc_staff_detail_df_with_invalid_values,
)


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


def test_handle_pqc_view_by_staff_detail_extract_pqc_data_arguments(monkeypatch):
    """
    handle_pqc_view_by_staff_detail should query PQC data for start_time as
    both the start and end date.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
        1,
    )


def test_handle_pqc_view_by_staff_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_pqc_view_by_staff_detail_filters_exact_name(monkeypatch):
    """
    Only rows whose Name exactly matches the requested name should be returned.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    assert len(result) == 3
    assert result["MachID"].tolist() == ["M3", "M4", "M1"]


def test_handle_pqc_view_by_staff_detail_sorts_and_formats_daterec(monkeypatch):
    """
    DateRec should be returned as ascending formatted strings.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    date_values = result["DateRec"].tolist()

    assert date_values == [
        "2026-05-01 07:10:00",
        "2026-05-01 07:30:00",
        "2026-05-01 07:40:00",
    ]
    assert all(isinstance(value, str) for value in date_values)
    assert result["id"].tolist() == [2, 3, 0]


def test_handle_pqc_view_by_staff_detail_strips_style_code(monkeypatch):
    """
    Style_Code values should be stripped after filtering and sorting.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_pqc_staff_detail_df_with_invalid_values(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    assert result["Style_Code"].tolist() == ["XYZ BLACK", "ABC RED"]


def test_handle_pqc_view_by_staff_detail_replaces_invalid_values(monkeypatch):
    """
    NaN, positive infinity, and negative infinity values should become None.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_pqc_staff_detail_df_with_invalid_values(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="Alice",
    )

    row_by_mach = {
        row["MachID"]: row
        for row in result.to_dict(orient="records")
    }

    assert row_by_mach["M1"]["brokenNDL"] is None
    assert row_by_mach["M1"]["dirty"] is None
    assert row_by_mach["M2"]["missNDL"] is None


def test_handle_pqc_view_by_staff_detail_no_matching_name_returns_empty_schema(
    monkeypatch,
):
    """
    A name with no matching rows should return an empty DataFrame with the
    same output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff_detail(
        start_time="2026-05-01",
        shift=1,
        name="No Match",
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS