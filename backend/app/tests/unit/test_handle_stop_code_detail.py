"""
Test cases for handle_stop_code_detail:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start_time, and end_time.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

4. Stop code filtering
   - Verify only matching Stop_code rows are included.

5. Basic aggregation
   - Verify freq, dur_sum, and dur_med are calculated per MachID and Style_Code.

6. Multiple machine/style grouping
   - Verify multiple MachID and Style_Code groups produce multiple output rows.

7. Style code normalization
   - Verify Style_Code is stripped and reduced to its first token.

8. Invalid Style_Code handling
   - Verify empty, None, and non-string Style_Code values are dropped by groupby.

9. Shift 1 filtering
   - Verify only day-shift rows are included.

10. Shift 2 filtering
    - Verify only night-shift rows are included.

11. All-shifts behavior
    - Verify shift values other than 1 and 2 include all shifts.

12. Shift boundary behavior
    - Verify 07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
      and 19:00:01 is night.

13. Sorting
    - Verify rows sort by MachID asc and freq desc.

14. Filtered-empty result
    - Verify filtering all rows returns an empty result with schema.

15. Median duration behavior
    - Verify odd and even sized groups calculate median durations correctly.
"""


from unittest.mock import Mock

import pandas as pd

import app.services.stop_view as stop_view

from app.tests.unit.mocks.common_mocks import patch_extract_base_data
from app.tests.unit.mocks.handle_stop_code_detail_mocks import (
    make_base_stop_code_detail_df,
    make_empty_stop_code_detail_df,
    make_stop_code_detail_filtered_empty_after_shift_df,
    make_stop_code_detail_median_duration_df,
    make_stop_code_detail_missing_style_df,
    make_stop_code_detail_multiple_groups_df,
    make_stop_code_detail_no_matching_stop_code_df,
    make_stop_code_detail_shift_boundary_df,
    make_stop_code_detail_shift_filter_df,
    make_stop_code_detail_sorting_df,
    make_stop_code_detail_stop_code_filter_df,
    make_stop_code_detail_style_normalization_df,
)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Style_Code",
    "freq",
    "dur_sum",
    "dur_med",
]


def _call_handle_stop_code_detail(shift=0, stop_code=10):
    return stop_view.handle_stop_code_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=shift,
        stop_code=stop_code,
    )


def test_handle_stop_code_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_code_detail_df(),
    )

    result = _call_handle_stop_code_detail()

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_stop_code_detail_extract_base_data_arguments(monkeypatch):
    """
    handle_stop_code_detail should call extract_base_data with StopExtractor,
    start_time, and end_time. Current behavior does not pass shift or stop_code.
    """
    raw_df = make_base_stop_code_detail_df()
    extract_mock = Mock(return_value=raw_df.copy())
    monkeypatch.setattr(stop_view, "extract_base_data", extract_mock)

    result = stop_view.handle_stop_code_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        stop_code=10,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        stop_view.StopExtractor,
        "2026-05-01 00:00:00",
        "2026-05-02 00:00:00",
    )


def test_handle_stop_code_detail_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_stop_code_detail should immediately return empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_code_detail_df(),
    )

    result = _call_handle_stop_code_detail()

    assert result.empty


def test_handle_stop_code_detail_filters_by_stop_code(monkeypatch):
    """
    Only rows matching the requested Stop_code should be aggregated.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_stop_code_filter_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)

    assert len(result) == 1
    row = result.iloc[0]
    assert row["MachID"] == 1
    assert row["Style_Code"] == "ABC"
    assert row["freq"] == 2
    assert row["dur_sum"] == pd.Timedelta(minutes=20)
    assert row["dur_med"] == pd.Timedelta(minutes=10)


def test_handle_stop_code_detail_basic_aggregation(monkeypatch):
    """
    Normal case:
    rows are grouped by MachID and normalized Style_Code.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_code_detail_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])

    mach_1_abc = result_by_mach_style.loc[(1, "ABC"), :]
    mach_2_abc = result_by_mach_style.loc[(2, "ABC"), :]

    assert len(result) == 2
    assert mach_1_abc["freq"] == 2
    assert mach_1_abc["dur_sum"] == pd.Timedelta(minutes=20)
    assert mach_1_abc["dur_med"] == pd.Timedelta(minutes=10)
    assert mach_2_abc["freq"] == 1
    assert mach_2_abc["dur_sum"] == pd.Timedelta(minutes=30)
    assert mach_2_abc["dur_med"] == pd.Timedelta(minutes=30)


def test_handle_stop_code_detail_multiple_machine_style_groups(monkeypatch):
    """
    Multiple machine and style groups should produce multiple output rows.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_multiple_groups_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])

    assert len(result) == 4
    assert result_by_mach_style.loc[(1, "ABC"), "freq"] == 2
    assert result_by_mach_style.loc[(1, "XYZ"), "freq"] == 1
    assert result_by_mach_style.loc[(2, "ABC"), "freq"] == 1
    assert result_by_mach_style.loc[(2, "XYZ"), "freq"] == 1


def test_handle_stop_code_detail_style_code_normalization(monkeypatch):
    """
    Style_Code should be stripped and reduced to its first whitespace token.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_style_normalization_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])

    assert len(result) == 3
    assert result_by_mach_style.loc[(1, "ABC"), "freq"] == 2
    assert result_by_mach_style.loc[(1, "XYZ"), "freq"] == 1
    assert result_by_mach_style.loc[(2, "ABC"), "freq"] == 1


def test_handle_stop_code_detail_invalid_style_code_is_dropped(monkeypatch):
    """
    Style_Code values like "", whitespace, None, and non-string values become
    None after cleaning. Pandas groupby drops NA groups by default.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_missing_style_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)

    assert len(result) == 1
    row = result.iloc[0]
    assert row["MachID"] == 1
    assert row["Style_Code"] == "ABC"
    assert row["freq"] == 1


def test_handle_stop_code_detail_shift_1_filters_day_shift(monkeypatch):
    """
    shift=1 should keep stops mapped to 07:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_shift_filter_df(),
    )

    result = _call_handle_stop_code_detail(shift=1, stop_code=10)

    assert set(result["Style_Code"]) == {"ABC"}
    assert result["freq"].sum() == 2
    assert result["dur_sum"].sum() == pd.Timedelta(minutes=30)


def test_handle_stop_code_detail_shift_2_filters_night_shift(monkeypatch):
    """
    shift=2 should keep stops mapped to 19:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_shift_filter_df(),
    )

    result = _call_handle_stop_code_detail(shift=2, stop_code=10)

    assert set(result["Style_Code"]) == {"ABC"}
    assert result["freq"].sum() == 3
    assert result["dur_sum"].sum() == pd.Timedelta(minutes=60)


def test_handle_stop_code_detail_other_shift_includes_all_shifts(monkeypatch):
    """
    Current behavior: shift values other than 1 or 2 do not filter rows by
    shift.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_shift_filter_df(),
    )

    result = _call_handle_stop_code_detail(shift=0, stop_code=10)

    assert set(result["Style_Code"]) == {"ABC"}
    assert result["freq"].sum() == 5
    assert result["dur_sum"].sum() == pd.Timedelta(minutes=90)


def test_handle_stop_code_detail_shift_boundaries(monkeypatch):
    """
    Current boundary behavior:
    07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
    and 19:00:01 is night.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_shift_boundary_df(),
    )

    day_result = _call_handle_stop_code_detail(shift=1, stop_code=10)
    night_result = _call_handle_stop_code_detail(shift=2, stop_code=10)

    assert day_result["freq"].sum() == 2
    assert day_result["dur_sum"].sum() == pd.Timedelta(minutes=35)
    assert night_result["freq"].sum() == 2
    assert night_result["dur_sum"].sum() == pd.Timedelta(minutes=35)


def test_handle_stop_code_detail_sorting(monkeypatch):
    """
    Rows should sort by MachID ascending and freq descending.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_sorting_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)

    assert list(result[["MachID", "Style_Code"]].itertuples(index=False, name=None)) == [
        (1, "ABC"),
        (1, "XYZ"),
        (2, "XYZ"),
        (2, "ABC"),
    ]
    assert list(result["freq"]) == [2, 1, 2, 1]
    assert list(result["id"]) == [0, 1, 2, 3]


def test_handle_stop_code_detail_filtered_empty_returns_schema(monkeypatch):
    """
    If filtering removes all rows after extraction, the result should be empty
    and keep the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_filtered_empty_after_shift_df(),
    )

    result = _call_handle_stop_code_detail(shift=1, stop_code=10)

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_stop_code_detail_no_matching_stop_code_returns_schema(
    monkeypatch,
):
    """
    If stop code filtering removes all rows, the result should be empty and
    keep the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_no_matching_stop_code_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_stop_code_detail_median_duration(monkeypatch):
    """
    Odd and even sized groups should calculate median duration correctly.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_code_detail_median_duration_df(),
    )

    result = _call_handle_stop_code_detail(stop_code=10)
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])

    assert result_by_mach_style.loc[(1, "ABC"), "dur_med"] == pd.Timedelta(minutes=15)
    assert result_by_mach_style.loc[(2, "XYZ"), "dur_med"] == pd.Timedelta(minutes=20)
