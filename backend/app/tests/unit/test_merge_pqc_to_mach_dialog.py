"""
Test cases for merge_pqc_to_mach_dialog:

1. Extractor arguments
   - Verify _extract_pqc_data receives start_time as both start and end time.

2. Output schema
   - Verify machine-info columns are preserved and PQC columns are appended.

3. Defect aggregation
   - Verify repeated PQC rows are grouped by MachID and Style_Code, with
     defects integer-divided by two.

4. Left merge behavior
   - Verify unmatched machine-info rows remain in the output.

5. Machine/style grouping key
   - Verify the same MachID with different Style_Code values is not collapsed.

6. Empty PQC data
   - Verify empty PQC data still returns the machine-info rows.

7. Zero shift validation
   - Verify shift zero raises the expected HTTPException before extraction.
"""

from unittest.mock import Mock

import pandas as pd
import pytest

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_mach_detail_df,
)
from app.tests.mocks.merge_pqc_to_mach_dialog_mocks import (
    make_base_mach_dialog_df,
    make_same_machine_different_style_dialog_df,
)


EXPECTED_APPENDED_COLUMNS = ["defects", "pqc_cnt"]


def _result_by_machine_style(result: pd.DataFrame) -> dict:
    return {
        (row["MachID"], row["Style_Code"]): row
        for row in result.to_dict(orient="records")
    }


def test_merge_pqc_to_mach_dialog_extract_pqc_data_arguments(monkeypatch):
    """
    merge_pqc_to_mach_dialog should request PQC rows for a single date/shift
    by passing start_time as both start and end time.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=make_base_mach_dialog_df(),
        start_time="2026-05-01",
        shift=1,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
        1,
    )


def test_merge_pqc_to_mach_dialog_output_columns(monkeypatch):
    """
    Machine-info columns from df should be preserved, and the PQC summary
    columns should be appended.
    """
    machine_df = make_base_mach_dialog_df()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=machine_df,
        start_time="2026-05-01",
        shift=1,
    )

    assert list(result.columns) == [
        *machine_df.columns.tolist(),
        *EXPECTED_APPENDED_COLUMNS,
    ]


def test_merge_pqc_to_mach_dialog_aggregates_defects_and_count(monkeypatch):
    """
    Repeated PQC rows for the same machine/style should be aggregated before
    merging onto the machine-info rows.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=make_base_mach_dialog_df(),
        start_time="2026-05-01",
        shift=1,
    )

    rows = _result_by_machine_style(result)

    assert rows[("M1", "ABC RED")]["pqc_cnt"] == 2
    assert rows[("M1", "ABC RED")]["defects"] == 2
    assert rows[("M2", "ABC BLUE")]["pqc_cnt"] == 1
    assert rows[("M2", "ABC BLUE")]["defects"] == 1
    assert rows[("M3", "XYZ BLACK")]["pqc_cnt"] == 1
    assert rows[("M3", "XYZ BLACK")]["defects"] == 0


def test_merge_pqc_to_mach_dialog_keeps_unmatched_machine_rows(monkeypatch):
    """
    The merge should be left-sided on the machine-info df, so machines without
    PQC rows stay present with null PQC metrics.
    """
    machine_df = make_base_mach_dialog_df()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=machine_df,
        start_time="2026-05-01",
        shift=1,
    )

    rows = _result_by_machine_style(result)

    assert result["MachID"].tolist() == machine_df["MachID"].tolist()
    assert rows[("M4", "QWE WHITE")]["Comment"] == "Low Ef"
    assert pd.isna(rows[("M4", "QWE WHITE")]["defects"])
    assert pd.isna(rows[("M4", "QWE WHITE")]["pqc_cnt"])


def test_merge_pqc_to_mach_dialog_groups_by_machine_and_full_style(monkeypatch):
    """
    MachID alone is not enough to match PQC rows. The full Style_Code must also
    match, so one machine row cannot inherit another style's PQC summary.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=make_same_machine_different_style_dialog_df(),
        start_time="2026-05-01",
        shift=1,
    )

    rows = _result_by_machine_style(result)

    assert rows[("M1", "ABC RED")]["pqc_cnt"] == 2
    assert rows[("M1", "ABC RED")]["defects"] == 2
    assert pd.isna(rows[("M1", "ABC BLUE")]["pqc_cnt"])
    assert pd.isna(rows[("M1", "ABC BLUE")]["defects"])
    assert rows[("M2", "ABC BLUE")]["pqc_cnt"] == 1
    assert rows[("M2", "ABC BLUE")]["defects"] == 1


def test_merge_pqc_to_mach_dialog_empty_pqc_data(monkeypatch):
    """
    Empty PQC data should still add the PQC columns and keep every machine
    row from the input df.
    """
    empty_pqc_df = make_base_pqc_mach_detail_df().iloc[0:0].copy()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        empty_pqc_df,
    )

    result = pqc_view.merge_pqc_to_mach_dialog(
        df=make_base_mach_dialog_df(),
        start_time="2026-05-01",
        shift=1,
    )

    assert len(result) == 4
    assert result["defects"].isna().all()
    assert result["pqc_cnt"].isna().all()


def test_merge_pqc_to_mach_dialog_shift_zero_raises(monkeypatch):
    """
    Shift zero is invalid for machine dialog PQC merging and should fail
    before attempting to extract PQC data.
    """
    extract_mock = Mock()
    monkeypatch.setattr(pqc_view, "_extract_pqc_data", extract_mock)

    with pytest.raises(pqc_view.HTTPException) as exc_info:
        pqc_view.merge_pqc_to_mach_dialog(
            df=make_base_mach_dialog_df(),
            start_time="2026-05-01",
            shift=0,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "shift can't be zero in mach dialog."
    extract_mock.assert_not_called()
