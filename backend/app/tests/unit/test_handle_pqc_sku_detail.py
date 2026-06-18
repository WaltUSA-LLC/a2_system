"""
Test cases for handle_pqc_sku_detail:

1. Extractor arguments
   - Verify _extract_pqc_data receives start as both start and end, plus shift.

2. Output schema
   - Verify the returned DataFrame has the expected columns.

3. Exact style filtering
   - Verify only rows matching the requested full Style_Code are included.

4. Machine aggregation
   - Verify repeated rows for the same shift, style, and machine are grouped.

5. Multiple machines
   - Verify one style can return multiple machine rows.

6. No matching style
   - Verify no matching Style_Code returns an empty result schema.

7. Shift formatting and sorting
   - Verify Shift_Start_Time is sorted and formatted as a string.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_sku_mach_detail_df,
    make_metrics_pqc_sku_mach_detail_df,
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
    "MachID",
    "pqc_cnt",
    *DEFECT_COLUMNS,
    "defects",
]


def _result_by_mach(result: pd.DataFrame) -> dict:
    return {
        row["MachID"]: row
        for row in result.to_dict(orient="records")
    }


def _result_by_mach_shift(result: pd.DataFrame) -> dict:
    return {
        (row["MachID"], row["Shift_Start_Time"]): row
        for row in result.to_dict(orient="records")
    }


def _make_same_style_multiple_mach_df() -> pd.DataFrame:
    df = make_base_pqc_sku_mach_detail_df()
    df.loc[df["Style_Code"] == "ABC BLUE", "Style_Code"] = "ABC RED"
    return df


def _make_same_style_multiple_shift_df() -> pd.DataFrame:
    df = make_base_pqc_sku_mach_detail_df()
    extra_shift_row = df[df["Style_Code"] == "ABC RED"].iloc[[0]].copy()
    extra_shift_row["Shift_Start_Time"] = pd.Timestamp("2026-05-01 19:00:00")
    return pd.concat([extra_shift_row, df], ignore_index=True)


def test_handle_pqc_sku_detail_extract_pqc_data_arguments(monkeypatch):
    """
    handle_pqc_sku_detail should query PQC data for start_time as both the
    start and end date.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="ABC RED",
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
        1,
    )


def test_handle_pqc_sku_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="ABC RED",
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_pqc_sku_detail_filters_exact_style(monkeypatch):
    """
    Only rows whose Style_Code exactly matches the requested style should be
    included before machine aggregation.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="ABC RED",
    )

    assert len(result) == 1
    assert result["MachID"].tolist() == ["M2"]


def test_handle_pqc_sku_detail_machine_aggregation(monkeypatch):
    """
    Rows with the same Shift_Start_Time and MachID should be aggregated into
    one machine row after style filtering.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="ABC RED",
    )

    row = result.iloc[0].to_dict()

    assert row["MachID"] == "M2"
    assert row["pqc_cnt"] == 2
    assert row["toeHole"] == 2
    assert row["brokenNDL"] == 1
    assert row["missNDL"] == 1
    assert row["defects"] == 4


def test_handle_pqc_sku_detail_multiple_machines_for_same_style(monkeypatch):
    """
    Matching rows for different machines should remain separate machine
    groups.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        _make_same_style_multiple_mach_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="ABC RED",
    )

    result_by_mach = _result_by_mach(result)

    assert set(result_by_mach) == {"M1", "M2"}
    assert result_by_mach["M1"]["pqc_cnt"] == 1
    assert result_by_mach["M1"]["defects"] == 2
    assert result_by_mach["M2"]["pqc_cnt"] == 2
    assert result_by_mach["M2"]["defects"] == 4


def test_handle_pqc_sku_detail_no_matching_style_returns_empty_schema(monkeypatch):
    """
    A style with no matching rows should return an empty DataFrame with the
    same output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=1,
        style="NO MATCH",
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_pqc_sku_detail_sorts_and_formats_shift_start_time(monkeypatch):
    """
    Shift_Start_Time should be returned as an ascending formatted string.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        _make_same_style_multiple_shift_df(),
    )

    result = pqc_view.handle_pqc_sku_detail(
        start_time="2026-05-01",
        shift=0,
        style="ABC RED",
    )

    shift_values = result["Shift_Start_Time"].tolist()
    result_by_mach_shift = _result_by_mach_shift(result)

    assert shift_values == sorted(shift_values)
    assert all(isinstance(value, str) for value in shift_values)
    assert set(shift_values) == {
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
    }
    assert result_by_mach_shift[("M2", "2026-05-01 07:00:00")]["pqc_cnt"] == 2
    assert result_by_mach_shift[("M2", "2026-05-01 19:00:00")]["pqc_cnt"] == 1
