"""
Test cases for handle_stop_view_by_code:

1. Output schemas
   - Verify the returned table and chart DataFrames have expected columns.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start_time, and end_time.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns five empty DataFrames.

4. Basic aggregation
   - Verify frequency, unique machine count, duration sum, and duration median.

5. Description trimming
   - Verify Stop_code rows with descriptions differing only by whitespace
     collapse into one group.

6. Duplicate machine count
   - Verify repeated MachID values are counted once in Mach_cnt.

7. Shift 1 filtering
   - Verify only day-shift rows are included.

8. Shift 2 filtering
   - Verify only night-shift rows are included.

9. All-shifts behavior
   - Verify shift values other than 1 and 2 include all rows.

10. Shift boundary behavior
    - Verify 07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
      and 19:00:01 is night.

11. Table sorting
    - Verify table rows sort by freq desc, Mach_cnt desc, and dur_sum desc.

12. Chart sorting
    - Verify each chart is sorted by its own metric.

13. Chart row cap
    - Verify chart outputs are capped at 11 rows.

14. Filtered-empty result
    - Verify shift filtering to zero rows returns empty post-aggregation
      outputs.

15. NaN Description handling
    - Verify NaN Description values are converted to Unknown.
"""

from unittest.mock import Mock

import pandas as pd

import app.services.stop_view as stop_view

from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.handle_stop_view_by_code_mocks import (
    make_base_stop_view_by_code_df,
    make_empty_stop_view_by_code_df,
    make_stop_view_by_code_chart_cap_df,
    make_stop_view_by_code_chart_sorting_df,
    make_stop_view_by_code_df_with_duplicate_mach,
    make_stop_view_by_code_filtered_empty_after_shift_df,
    make_stop_view_by_code_nan_description_df,
    make_stop_view_by_code_shift_boundary_df,
    make_stop_view_by_code_shift_filter_df,
    make_stop_view_by_code_sorting_df,
)


EXPECTED_TABLE_COLUMNS = [
    "id",
    "Stop_code",
    "Description",
    "Mach_cnt",
    "freq",
    "dur_sum",
    "dur_med",
]

EXPECTED_FREQ_CHART_COLUMNS = ["Stop_code", "Description", "freq"]
EXPECTED_MACH_CHART_COLUMNS = ["Stop_code", "Description", "Mach_cnt"]
EXPECTED_DUR_SUM_CHART_COLUMNS = ["Stop_code", "Description", "dur_sum"]
EXPECTED_DUR_MED_CHART_COLUMNS = ["Stop_code", "Description", "dur_med"]


def _call_handle_stop_view_by_code(shift=0):
    return stop_view.handle_stop_view_by_code(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=shift,
    )


def test_handle_stop_view_by_code_output_columns(monkeypatch):
    """
    Test final output schemas for the main table and chart DataFrames.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_code_df(),
    )

    result, chart_freq, chart_mach, chart_dur_sum, chart_dur_med = (
        _call_handle_stop_view_by_code()
    )

    assert list(result.columns) == EXPECTED_TABLE_COLUMNS
    assert list(chart_freq.columns) == EXPECTED_FREQ_CHART_COLUMNS
    assert list(chart_mach.columns) == EXPECTED_MACH_CHART_COLUMNS
    assert list(chart_dur_sum.columns) == EXPECTED_DUR_SUM_CHART_COLUMNS
    assert list(chart_dur_med.columns) == EXPECTED_DUR_MED_CHART_COLUMNS


def test_handle_stop_view_by_code_extract_base_data_arguments(monkeypatch):
    """
    handle_stop_view_by_code should call extract_base_data with StopExtractor,
    start_time, and end_time. Current behavior does not pass shift.
    """
    raw_df = make_base_stop_view_by_code_df()
    extract_mock = Mock(return_value=raw_df.copy())
    monkeypatch.setattr(stop_view, "extract_base_data", extract_mock)

    result, *_ = stop_view.handle_stop_view_by_code(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        stop_view.StopExtractor,
        "2026-05-01 00:00:00",
        "2026-05-02 00:00:00",
    )


def test_handle_stop_view_by_code_empty_df(monkeypatch):
    """
    If extract_base_data returns an empty DataFrame, the function should
    return five empty DataFrames immediately.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_view_by_code_df(),
    )

    outputs = _call_handle_stop_view_by_code()

    assert len(outputs) == 5
    assert all(output.empty for output in outputs)


def test_handle_stop_view_by_code_basic_aggregation(monkeypatch):
    """
    Normal case: rows are grouped by Stop_code and trimmed Description.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_code_df(),
    )

    result, *_ = _call_handle_stop_view_by_code()
    result_by_code = result.set_index("Stop_code")

    jam = result_by_code.loc[10, :]
    low_air = result_by_code.loc[20, :]

    assert jam["Description"] == "Jam"
    assert jam["Mach_cnt"] == 2
    assert jam["freq"] == 2
    assert jam["dur_sum"] == pd.Timedelta(minutes=30)
    assert jam["dur_med"] == pd.Timedelta(minutes=15)

    assert low_air["Description"] == "Low Air"
    assert low_air["Mach_cnt"] == 1
    assert low_air["freq"] == 1
    assert low_air["dur_sum"] == pd.Timedelta(minutes=5)
    assert low_air["dur_med"] == pd.Timedelta(minutes=5)


def test_handle_stop_view_by_code_trims_description(monkeypatch):
    """
    Descriptions that differ only by leading/trailing whitespace should be
    grouped together after stripping.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_code_df(),
    )

    result, *_ = _call_handle_stop_view_by_code()

    assert len(result[result["Stop_code"] == 10]) == 1
    row = result[result["Stop_code"] == 10].iloc[0]
    assert row["Description"] == "Jam"
    assert row["freq"] == 2


def test_handle_stop_view_by_code_nan_description_becomes_unknown(monkeypatch):
    """
    NaN descriptions should be converted to Unknown before grouping and
    included in table and chart outputs.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_nan_description_df(),
    )

    result, chart_freq, chart_mach, chart_dur_sum, chart_dur_med = (
        _call_handle_stop_view_by_code()
    )

    unknown_rows = result[result["Description"] == "Unknown"]

    assert len(unknown_rows) == 1
    row = unknown_rows.iloc[0]
    assert row["Stop_code"] == 10
    assert row["Mach_cnt"] == 1
    assert row["freq"] == 1
    assert row["dur_sum"] == pd.Timedelta(minutes=10)
    assert row["dur_med"] == pd.Timedelta(minutes=10)

    assert "Unknown" in set(chart_freq["Description"])
    assert "Unknown" in set(chart_mach["Description"])
    assert "Unknown" in set(chart_dur_sum["Description"])
    assert "Unknown" in set(chart_dur_med["Description"])


def test_handle_stop_view_by_code_duplicate_mach_counted_once(monkeypatch):
    """
    Repeated MachID values in a stop-code group should count once.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_df_with_duplicate_mach(),
    )

    result, *_ = _call_handle_stop_view_by_code()
    row = result.iloc[0]

    assert row["Stop_code"] == 10
    assert row["freq"] == 3
    assert row["Mach_cnt"] == 2
    assert row["dur_sum"] == pd.Timedelta(minutes=60)
    assert row["dur_med"] == pd.Timedelta(minutes=20)


def test_handle_stop_view_by_code_shift_1_filters_day_shift(monkeypatch):
    """
    shift=1 should keep stops mapped to 07:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_shift_filter_df(),
    )

    result, *_ = _call_handle_stop_view_by_code(shift=1)

    assert set(result["Stop_code"]) == {20, 30}
    assert "Day Start" in set(result["Description"])
    assert "Day End" in set(result["Description"])


def test_handle_stop_view_by_code_shift_2_filters_night_shift(monkeypatch):
    """
    shift=2 should keep stops mapped to 19:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_shift_filter_df(),
    )

    result, *_ = _call_handle_stop_view_by_code(shift=2)

    assert set(result["Stop_code"]) == {10, 40, 50}
    assert "Night Previous" in set(result["Description"])
    assert "Night Start" in set(result["Description"])
    assert "Night End" in set(result["Description"])


def test_handle_stop_view_by_code_other_shift_includes_all_rows(monkeypatch):
    """
    Current behavior: shift values other than 1 or 2 do not filter rows.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_shift_filter_df(),
    )

    result, *_ = _call_handle_stop_view_by_code(shift=0)

    assert set(result["Stop_code"]) == {10, 20, 30, 40, 50}


def test_handle_stop_view_by_code_shift_boundaries(monkeypatch):
    """
    Current boundary behavior:
    07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
    and 19:00:01 is night.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_shift_boundary_df(),
    )

    day_result, *_ = _call_handle_stop_view_by_code(shift=1)
    night_result, *_ = _call_handle_stop_view_by_code(shift=2)

    assert set(day_result["Stop_code"]) == {20, 30}
    assert set(night_result["Stop_code"]) == {10, 40}


def test_handle_stop_view_by_code_table_sorting(monkeypatch):
    """
    Table rows should sort by freq desc, Mach_cnt desc, dur_sum desc.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_sorting_df(),
    )

    result, *_ = _call_handle_stop_view_by_code()

    assert list(result["Stop_code"]) == [20, 10, 30]
    assert list(result["id"]) == [0, 1, 2]


def test_handle_stop_view_by_code_chart_sorting(monkeypatch):
    """
    Chart DataFrames should be sorted independently by their selected metric.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_chart_sorting_df(),
    )

    _, chart_freq, chart_mach, chart_dur_sum, chart_dur_med = (
        _call_handle_stop_view_by_code()
    )

    assert list(chart_freq["Stop_code"]) == [10, 20, 30]
    assert list(chart_mach["Stop_code"]) == [10, 20, 30]
    assert list(chart_dur_sum["Stop_code"]) == [30, 20, 10]
    assert list(chart_dur_med["Stop_code"]) == [30, 20, 10]


def test_handle_stop_view_by_code_chart_row_cap(monkeypatch):
    """
    Chart outputs should be capped at 11 rows.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_chart_cap_df(),
    )

    _, chart_freq, chart_mach, chart_dur_sum, chart_dur_med = (
        _call_handle_stop_view_by_code()
    )

    assert len(chart_freq) == 11
    assert len(chart_mach) == 11
    assert len(chart_dur_sum) == 11
    assert len(chart_dur_med) == 11


def test_handle_stop_view_by_code_filtered_empty_after_shift(monkeypatch):
    """
    If shift filtering removes all rows, post-aggregation outputs should be
    empty and keep their final schemas.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_code_filtered_empty_after_shift_df(),
    )

    result, chart_freq, chart_mach, chart_dur_sum, chart_dur_med = (
        _call_handle_stop_view_by_code(shift=1)
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_TABLE_COLUMNS
    assert chart_freq.empty
    assert chart_mach.empty
    assert chart_dur_sum.empty
    assert chart_dur_med.empty
