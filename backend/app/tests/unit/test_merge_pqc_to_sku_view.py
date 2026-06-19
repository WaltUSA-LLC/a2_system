"""
Test cases for merge_pqc_to_sku_view:

1. Extractor arguments
   - Verify _extract_pqc_data receives start_time, end_time, and shift.

2. Output schema
   - Verify SKU-info columns are preserved and PQC columns are appended.

3. Style normalization and aggregation
   - Verify PQC Style_Code values are reduced to the first upper-case token
     before grouping.

4. SKU and shift grouping
   - Verify PQC rows are grouped by normalized Style_Code and Shift_Start_Time.

5. Left merge behavior
   - Verify unmatched SKU-info rows remain in the output.

6. Empty PQC data
   - Verify empty PQC data still returns the SKU-info rows.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_sku_mach_detail_df,
    make_multi_pqc_shift_df,
)
from app.tests.mocks.merge_pqc_to_sku_view_mocks import (
    make_base_sku_view_df,
    make_multi_sku_shift_view_df,
    make_sku_view_df_with_unmatched_rows,
)


EXPECTED_APPENDED_COLUMNS = ["defects", "pqc_cnt"]


def _result_by_sku_shift(result: pd.DataFrame) -> dict:
    return {
        (row["Style_Code"], row["Shift_Start_Time"]): row
        for row in result.to_dict(orient="records")
    }


def test_merge_pqc_to_sku_view_extract_pqc_data_arguments(monkeypatch):
    """
    merge_pqc_to_sku_view should pass the requested date range and shift to
    _extract_pqc_data.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=make_base_sku_view_df(),
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


def test_merge_pqc_to_sku_view_output_columns(monkeypatch):
    """
    SKU-info columns from df should be preserved, and the PQC summary columns
    should be appended.
    """
    sku_df = make_base_sku_view_df()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=sku_df,
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == [
        *sku_df.columns.tolist(),
        *EXPECTED_APPENDED_COLUMNS,
    ]


def test_merge_pqc_to_sku_view_normalizes_pqc_style_before_grouping(monkeypatch):
    """
    Full PQC styles such as ABC RED and ABC BLUE should merge into the ABC SKU
    row after the helper normalizes Style_Code to the first upper-case token.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=make_base_sku_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    rows = _result_by_sku_shift(result)
    shift_time = pd.Timestamp("2026-05-01 07:00:00")

    assert rows[("ABC", shift_time)]["pqc_cnt"] == 3
    assert rows[("ABC", shift_time)]["defects"] == 3
    assert ("ABC RED", shift_time) not in rows
    assert ("ABC BLUE", shift_time) not in rows


def test_merge_pqc_to_sku_view_groups_by_sku_and_shift(monkeypatch):
    """
    SKU and Shift_Start_Time together define the PQC summary key. The same SKU
    on another shift should not receive this shift's PQC metrics.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_multi_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=make_multi_sku_shift_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    rows = _result_by_sku_shift(result)
    shift_1 = pd.Timestamp("2026-05-01 07:00:00")
    shift_2 = pd.Timestamp("2026-05-01 19:00:00")

    assert rows[("ABC", shift_1)]["pqc_cnt"] == 2
    assert rows[("ABC", shift_1)]["defects"] == 2
    assert rows[("XYZ", shift_2)]["pqc_cnt"] == 2
    assert rows[("XYZ", shift_2)]["defects"] == 2
    assert rows[("QWE", shift_2)]["pqc_cnt"] == 1
    assert rows[("QWE", shift_2)]["defects"] == 1


def test_merge_pqc_to_sku_view_keeps_unmatched_sku_rows(monkeypatch):
    """
    The merge should be left-sided on the SKU-info df, so SKU/shift rows
    without PQC data stay present with null PQC metrics.
    """
    sku_df = make_sku_view_df_with_unmatched_rows()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_multi_pqc_shift_df(),
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=sku_df,
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    rows = _result_by_sku_shift(result)
    unmatched_same_sku_row = rows[
        ("ABC", pd.Timestamp("2026-05-01 19:00:00"))
    ]
    unmatched_missing_sku_row = rows[
        ("MISSING", pd.Timestamp("2026-05-02 07:00:00"))
    ]

    assert result["Style_Code"].tolist() == sku_df["Style_Code"].tolist()
    assert unmatched_same_sku_row["Mach_cnt"] == 1
    assert pd.isna(unmatched_same_sku_row["defects"])
    assert pd.isna(unmatched_same_sku_row["pqc_cnt"])
    assert unmatched_missing_sku_row["Efficiency"] == 0.3
    assert pd.isna(unmatched_missing_sku_row["defects"])
    assert pd.isna(unmatched_missing_sku_row["pqc_cnt"])


def test_merge_pqc_to_sku_view_empty_pqc_data(monkeypatch):
    """
    Empty PQC data should still add the PQC columns and keep every SKU row from
    the input df.
    """
    empty_pqc_df = make_base_pqc_sku_mach_detail_df().iloc[0:0].copy()
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        empty_pqc_df,
    )

    result = pqc_view.merge_pqc_to_sku_view(
        df=make_base_sku_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert len(result) == 3
    assert result["defects"].isna().all()
    assert result["pqc_cnt"].isna().all()
