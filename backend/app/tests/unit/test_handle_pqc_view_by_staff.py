"""
Test cases for handle_pqc_view_by_staff:

1. Extractor arguments
   - Verify _extract_pqc_data receives start, end, and shift.

2. Output schema
   - Verify the returned DataFrame has the expected columns.

3. Staff aggregation
   - Verify repeated rows for the same shift, name, and role are grouped.

4. Name and role grouping
   - Verify the same staff name in different roles remains separate.

5. Check-window metrics
   - Verify start_check, end_check, and avg_adj_diff use threshold-filtered
     DateRec intervals.

6. Single-record average interval
   - Verify one-record groups produce NaT avg_adj_diff.

7. Defect totals
   - Verify defects are summed from raw defect columns and are not halved.

8. Shift formatting and sorting
   - Verify Shift_Start_Time is sorted and formatted as a string.

9. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty DataFrame.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_staff_df,
    make_multi_pqc_staff_shift_df,
    make_pqc_staff_df_with_threshold_intervals,
)


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


def _result_by_staff(result: pd.DataFrame) -> dict:
    return {
        (row["Name"], row["Role"]): row
        for row in result.to_dict(orient="records")
    }


def _result_by_staff_shift(result: pd.DataFrame) -> dict:
    return {
        (row["Name"], row["Role"], row["Shift_Start_Time"]): row
        for row in result.to_dict(orient="records")
    }


def test_handle_pqc_view_by_staff_extract_pqc_data_arguments(monkeypatch):
    """
    handle_pqc_view_by_staff should pass the requested date range and shift to
    _extract_pqc_data.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_handle_pqc_view_by_staff_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_pqc_view_by_staff_staff_aggregation(monkeypatch):
    """
    Rows with the same Shift_Start_Time, Name, and Role should be aggregated
    into one staff row.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    alice_ko = _result_by_staff(result)[("Alice", "KO")]

    assert alice_ko["pqc_cnt"] == 2
    assert alice_ko["toeHole"] == 1
    assert alice_ko["brokenNDL"] == 1
    assert alice_ko["missNDL"] == 1
    assert alice_ko["missYarn"] == 1
    assert alice_ko["defects"] == 4


def test_handle_pqc_view_by_staff_groups_by_name_and_role(monkeypatch):
    """
    The same Name in different Role values should produce separate output
    rows.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    result_by_staff = _result_by_staff(result)

    assert set(result_by_staff) == {
        ("Alice", "KO"),
        ("Alice", "Tech"),
        ("Bob", "Tech"),
    }
    assert result_by_staff[("Alice", "KO")]["pqc_cnt"] == 2
    assert result_by_staff[("Alice", "Tech")]["pqc_cnt"] == 1


def test_handle_pqc_view_by_staff_check_window_metrics(monkeypatch):
    """
    start_check and end_check should use all DateRec values, while
    avg_adj_diff should only average adjacent gaps above PQC_FREQ_THRESHOLD.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_pqc_staff_df_with_threshold_intervals(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    alice_ko = _result_by_staff(result)[("Alice", "KO")]

    assert alice_ko["start_check"] == "07:10:00"
    assert alice_ko["end_check"] == "08:30:00"
    assert alice_ko["avg_adj_diff"] == pd.Timedelta(minutes=30)


def test_handle_pqc_view_by_staff_single_record_avg_adj_diff_is_nat(monkeypatch):
    """
    A group with one DateRec value has no adjacent interval to average.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    bob_tech = _result_by_staff(result)[("Bob", "Tech")]

    assert bob_tech["start_check"] == "07:20:00"
    assert bob_tech["end_check"] == "07:20:00"
    assert pd.isna(bob_tech["avg_adj_diff"])


def test_handle_pqc_view_by_staff_defects_are_not_halved(monkeypatch):
    """
    handle_pqc_view_by_staff reports raw PQC defect totals. It should not
    apply the integer division used by PQC merge helpers.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_staff_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    alice_ko = _result_by_staff(result)[("Alice", "KO")]

    assert alice_ko["defects"] == 4


def test_handle_pqc_view_by_staff_sorts_and_formats_shift_start_time(monkeypatch):
    """
    Shift_Start_Time should be returned as an ascending formatted string.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_multi_pqc_staff_shift_df(),
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    shift_values = result["Shift_Start_Time"].tolist()
    result_by_staff_shift = _result_by_staff_shift(result)

    assert shift_values == sorted(shift_values)
    assert all(isinstance(value, str) for value in shift_values)
    assert set(shift_values) == {
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
    }
    assert result_by_staff_shift[
        ("Alice", "KO", "2026-05-01 07:00:00")
    ]["pqc_cnt"] == 2
    assert result_by_staff_shift[
        ("Alice", "KO", "2026-05-01 19:00:00")
    ]["pqc_cnt"] == 1


def test_handle_pqc_view_by_staff_empty_df(monkeypatch):
    """
    Empty _extract_pqc_data output should return an empty DataFrame.
    """
    empty_df = make_base_pqc_staff_df().iloc[0:0].copy()
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        empty_df,
    )

    result = pqc_view.handle_pqc_view_by_staff(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result.empty
    assert list(result.columns) == []
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
        1,
    )
