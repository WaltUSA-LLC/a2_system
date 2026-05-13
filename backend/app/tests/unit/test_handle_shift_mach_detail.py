"""
Test cases for handle_shift_mach_detail:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Extractor arguments
   - Verify extract_base_data receives start_time as both start and end time.

3. Invoked helper functions
   - Verify handle_shift_mach_detail calls expected dependency/helper
     functions.

4. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

5. Shift_Start_Time formatting
   - Verify Shift_Start_Time is converted from pandas Timestamp to string.

6. Metric calculations
   - Verify MES_prs, ON_Time_Occupation, and Mach_Efficiency calculations.

7. Comment assignment
   - Verify Mach_Efficiency >= 0.8 is Good and < 0.8 is Low Ef.

8. Shutdown machine filtering
   - Verify filterShutdownMach removes rows before estimator calls.

9. Filtered-empty result
   - Verify filtering all rows returns an empty DataFrame.

10. Duplicate machine rows
    - Verify repeated MachID rows are preserved and not aggregated.

11. Row order
    - Verify output preserves source row order after filtering.

12. Null and infinite value handling
    - Verify zero-time, zero-ST, and NaN-ST current behavior.
"""


from unittest.mock import Mock

import numpy as np
import pytest

import app.services.shift_view as shift_view

from app.tests.mocks.common_mocks import (
    make_call_counting_mocks,
    patch_common_dependencies,
    patch_extract_base_data,
)

from app.tests.mocks.handle_shift_mach_detail_mocks import (
    make_base_shift_mach_detail_df,
    make_empty_shift_mach_detail_df,
    make_shift_mach_detail_df_for_filter_shutdown,
    make_shift_mach_detail_df_for_metrics_and_comments,
    make_shift_mach_detail_df_that_filters_to_empty,
    make_shift_mach_detail_df_with_duplicate_mach,
    make_shift_mach_detail_df_with_nan_st_prs,
    make_shift_mach_detail_df_with_zero_time,
    make_unsorted_shift_mach_detail_df,
)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Shift_Start_Time",
    "Style_Code",
    "Weight",
    "MES_prs",
    "NAU_prs",
    "ON_Time",
    "OFF_Time",
    "ON_Time_Occupation",
    "Mach_Efficiency",
    "Comment",
]


def _filter_marked_shutdown_mach(df):
    filtered_df = df[~df["Should_Filter"]].copy()
    return filtered_df.drop(columns=["Should_Filter"])


def test_handle_shift_mach_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_shift_mach_detail_extract_base_data_arguments(monkeypatch):
    """
    handle_shift_mach_detail should request one shift by passing start_time as
    both the start and end time to extract_base_data.
    """
    raw_df = make_base_shift_mach_detail_df()
    extract_mock = Mock(return_value=raw_df.copy())
    monkeypatch.setattr(shift_view, "extract_base_data", extract_mock)

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=2,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        shift_view.MESExtractor,
        "2026-05-01 00:00:00",
        "2026-05-01 00:00:00",
        2,
    )


def test_handle_shift_mach_detail_calls_invoked_functions(monkeypatch):
    """
    Verify that handle_shift_mach_detail calls the invoked helper functions.
    This test focuses on wiring, not calculation correctness.
    """
    raw_df = make_base_shift_mach_detail_df()

    patch_extract_base_data(
        monkeypatch,
        shift_view,
        raw_df,
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert not result.empty
    mocks["distributeWeightForSameMach"].assert_called_once()
    mocks["clean_weight"].assert_called_once()
    mocks["filterShutdownMach"].assert_called_once()
    assert mocks["estimate_mes_output_prs"].call_count == len(raw_df)
    assert mocks["estimate_st_output_prs"].call_count == len(raw_df)


def test_handle_shift_mach_detail_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_shift_mach_detail should immediately return empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_empty_shift_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert result.empty
    mocks["distributeWeightForSameMach"].assert_not_called()
    mocks["clean_weight"].assert_not_called()
    mocks["filterShutdownMach"].assert_not_called()
    mocks["estimate_mes_output_prs"].assert_not_called()
    mocks["estimate_st_output_prs"].assert_not_called()


def test_handle_shift_mach_detail_shift_start_time_is_string(monkeypatch):
    """
    Shift_Start_Time should be converted from Timestamp to string.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    row = result.iloc[0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"


def test_handle_shift_mach_detail_calculates_metrics(monkeypatch):
    """
    Verify machine-level MES output, ON time occupation, and efficiency
    calculations.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_for_metrics_and_comments(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc["M_GOOD", "MES_prs"] == 9
    assert result_by_mach.loc["M_GOOD", "ON_Time_Occupation"] == pytest.approx(0.9)
    assert result_by_mach.loc["M_GOOD", "Mach_Efficiency"] == pytest.approx(0.9)

    assert result_by_mach.loc["M_BOUNDARY", "MES_prs"] == 8
    assert result_by_mach.loc["M_BOUNDARY", "ON_Time_Occupation"] == pytest.approx(0.8)
    assert result_by_mach.loc["M_BOUNDARY", "Mach_Efficiency"] == pytest.approx(0.8)

    assert result_by_mach.loc["M_LOW", "MES_prs"] == 1
    assert result_by_mach.loc["M_LOW", "ON_Time_Occupation"] == pytest.approx(0.333)
    assert result_by_mach.loc["M_LOW", "Mach_Efficiency"] == pytest.approx(0.333)


def test_handle_shift_mach_detail_comment_good_and_low_eff(monkeypatch):
    """
    Machines with efficiency >= 0.8 should be Good.
    Machines with efficiency < 0.8 should be Low Ef.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_for_metrics_and_comments(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc["M_GOOD", "Comment"] == "Good"
    assert result_by_mach.loc["M_BOUNDARY", "Comment"] == "Good"
    assert result_by_mach.loc["M_LOW", "Comment"] == "Low Ef"


def test_handle_shift_mach_detail_filter_shutdown_mach_affects_rows(
    monkeypatch,
):
    """
    filterShutdownMach should remove rows before throughput and efficiency
    calculations are applied.
    """
    raw_df = make_shift_mach_detail_df_for_filter_shutdown()

    patch_extract_base_data(
        monkeypatch,
        shift_view,
        raw_df,
    )

    mocks = make_call_counting_mocks()
    mocks["filterShutdownMach"] = Mock(
        side_effect=_filter_marked_shutdown_mach
    )
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert len(result) == 2
    assert list(result["MachID"]) == ["M_KEEP_1", "M_KEEP_2"]
    assert "M_STOP" not in set(result["MachID"])
    assert mocks["estimate_mes_output_prs"].call_count == 2
    assert mocks["estimate_st_output_prs"].call_count == 2


def test_handle_shift_mach_detail_filtered_empty_returns_empty(
    monkeypatch,
):
    """
    If filterShutdownMach removes all rows, handle_shift_mach_detail should
    return an empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_that_filters_to_empty(),
    )

    mocks = make_call_counting_mocks()
    mocks["filterShutdownMach"] = Mock(
        side_effect=_filter_marked_shutdown_mach
    )
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert result.empty
    mocks["estimate_mes_output_prs"].assert_not_called()
    mocks["estimate_st_output_prs"].assert_not_called()


def test_handle_shift_mach_detail_duplicate_mach_rows_are_preserved(
    monkeypatch,
):
    """
    Repeated MachID values should remain separate rows, not be aggregated.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_with_duplicate_mach(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert len(result) == 3
    assert list(result["MachID"]) == ["M1", "M1", "M2"]
    assert list(result["Weight"]) == [7, 5, 6]
    assert list(result["NAU_prs"]) == [5, 3, 4]


def test_handle_shift_mach_detail_ascending_row_order(monkeypatch):
    """
    Current behavior: output ascending preserves row order by MachID.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_unsorted_shift_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    assert list(result["MachID"]) == ["M1", "M2", "M3"]


def test_handle_shift_mach_detail_zero_time_becomes_none(monkeypatch):
    """
    If ON_Time + OFF_Time is 0, ON_Time_Occupation becomes NaN.
    The final null conversion should convert it to None.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_with_zero_time(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    row = result.iloc[0]

    assert row["ON_Time_Occupation"] is None
    assert row["Mach_Efficiency"] == pytest.approx(0.5)
    assert row["Comment"] == "Low Ef"


def test_handle_shift_mach_detail_nan_st_prs_becomes_none(monkeypatch):
    """
    If ST_prs is NaN, Mach_Efficiency becomes None and the comment remains
    the initial empty string.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_with_nan_st_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )

    result = shift_view.handle_shift_mach_detail(
        start_time="2026-05-01 00:00:00",
        shift=1,
    )

    row = result.iloc[0]

    assert row["Mach_Efficiency"] is None
    assert row["Comment"] == ""