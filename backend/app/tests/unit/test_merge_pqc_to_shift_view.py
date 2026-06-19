"""
Test cases for merge_pqc_to_shift_view:

1. Extractor arguments
   - Verify _extract_pqc_data receives start_time, end_time, and shift.

2. Output schema
   - Verify shift-info columns are preserved and PQC columns are appended.

3. Defect aggregation
   - Verify PQC rows are grouped by Shift_Start_Time, with defects
     integer-divided by two.

4. Multiple shifts
   - Verify separate Shift_Start_Time values receive separate PQC summaries.

5. Left merge behavior
   - Verify unmatched shift-info rows remain in the output.

6. Empty PQC data
   - Verify empty PQC data still returns the shift-info rows.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_shift_df,
    make_multi_pqc_shift_df,
)
from app.tests.mocks.merge_pqc_to_shift_view_mocks import (
    make_base_shift_view_df,
    make_multi_shift_view_df,
    make_shift_view_df_with_unmatched_shift,
)


EXPECTED_APPENDED_COLUMNS = ["defects", "pqc_cnt"]


def _result_by_shift(result: pd.DataFrame) -> dict:
    return {
        row["Shift_Start_Time"]: row
        for row in result.to_dict(orient="records")
    }


def test_merge_pqc_to_shift_view_extract_pqc_data_arguments(monkeypatch):
    """
    merge_pqc_to_shift_view should pass the requested date range and shift to
    _extract_pqc_data.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=make_base_shift_view_df(),
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


def test_merge_pqc_to_shift_view_output_columns(monkeypatch):
    """
    Shift-info columns from df should be preserved, and the PQC summary
    columns should be appended.
    """
    shift_df = make_base_shift_view_df()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=shift_df,
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == [
        *shift_df.columns.tolist(),
        *EXPECTED_APPENDED_COLUMNS,
    ]


def test_merge_pqc_to_shift_view_aggregates_defects_and_count(monkeypatch):
    """
    PQC rows from the same shift should be aggregated before merging onto the
    shift-info row.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=make_base_shift_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    row = result.iloc[0]

    assert row["pqc_cnt"] == 2
    assert row["defects"] == 2


def test_merge_pqc_to_shift_view_groups_multiple_shifts(monkeypatch):
    """
    Different Shift_Start_Time values should receive separate PQC summaries.
    Style_Code and MachID should not split the shift-level grouping.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_multi_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=make_multi_shift_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    rows = _result_by_shift(result)

    assert rows[pd.Timestamp("2026-05-01 07:00:00")]["pqc_cnt"] == 2
    assert rows[pd.Timestamp("2026-05-01 07:00:00")]["defects"] == 2
    assert rows[pd.Timestamp("2026-05-01 19:00:00")]["pqc_cnt"] == 3
    assert rows[pd.Timestamp("2026-05-01 19:00:00")]["defects"] == 3


def test_merge_pqc_to_shift_view_keeps_unmatched_shift_rows(monkeypatch):
    """
    The merge should be left-sided on the shift-info df, so shifts without PQC
    rows stay present with null PQC metrics.
    """
    shift_df = make_shift_view_df_with_unmatched_shift()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_multi_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=shift_df,
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    rows = _result_by_shift(result)
    unmatched_row = rows[pd.Timestamp("2026-05-02 07:00:00")]

    assert result["Shift_Start_Time"].tolist() == shift_df["Shift_Start_Time"].tolist()
    assert unmatched_row["Mach_cnt"] == 1
    assert pd.isna(unmatched_row["defects"])
    assert pd.isna(unmatched_row["pqc_cnt"])


def test_merge_pqc_to_shift_view_empty_pqc_data(monkeypatch):
    """
    Empty PQC data should still add the PQC columns and keep every shift row
    from the input df.
    """
    empty_pqc_df = make_base_pqc_shift_df().iloc[0:0].copy()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        empty_pqc_df,
    )

    result = pqc_view.merge_pqc_to_shift_view(
        df=make_multi_shift_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert len(result) == 2
    assert result["defects"].isna().all()
    assert result["pqc_cnt"].isna().all()
