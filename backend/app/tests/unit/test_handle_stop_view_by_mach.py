"""
Test cases for handle_stop_view_by_mach:

1. Output schemas
   - Verify the returned table and chart DataFrames have expected columns.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start_time, and end_time.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns two empty DataFrames.

4. Basic aggregation
   - Verify table frequency by machine/style and chart frequency by machine,
     independent of Stop_code and duration.

5. Style code normalization
   - Verify Style_Code is stripped and reduced to its first token.

6. Missing style behavior
   - Verify blank, None, and non-string Style_Code values are excluded from
     table grouping but still counted in the machine chart.

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
    - Verify table rows sort by MachID asc, Style_Code asc, and freq desc.

12. Chart sorting
    - Verify chart rows sort by freq desc.

13. Chart row cap
    - Verify chart output is capped at 10 rows.

14. Filtered-empty result
    - Verify shift filtering to zero rows returns empty post-aggregation
      outputs with final schemas.
"""

from unittest.mock import Mock

import app.services.stop_view as stop_view

from app.tests.unit.mocks.common_mocks import patch_extract_base_data
from app.tests.unit.mocks.handle_stop_view_by_mach_mocks import (
    make_base_stop_view_by_mach_df,
    make_empty_stop_view_by_mach_df,
    make_stop_view_by_mach_chart_cap_df,
    make_stop_view_by_mach_chart_sorting_df,
    make_stop_view_by_mach_filtered_empty_after_shift_df,
    make_stop_view_by_mach_missing_style_df,
    make_stop_view_by_mach_shift_boundary_df,
    make_stop_view_by_mach_shift_filter_df,
    make_stop_view_by_mach_style_normalization_df,
    make_stop_view_by_mach_table_sorting_df,
)


EXPECTED_TABLE_COLUMNS = ["id", "MachID", "Style_Code", "freq"]
EXPECTED_CHART_COLUMNS = ["MachID", "freq"]


def _call_handle_stop_view_by_mach(shift=0):
    return stop_view.handle_stop_view_by_mach(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=shift,
    )


def test_handle_stop_view_by_mach_output_columns(monkeypatch):
    """
    Test final output schemas for the main table and chart DataFrames.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_view_by_mach_df(),
    )

    result, chart = _call_handle_stop_view_by_mach()

    assert list(result.columns) == EXPECTED_TABLE_COLUMNS
    assert list(chart.columns) == EXPECTED_CHART_COLUMNS


def test_handle_stop_view_by_mach_extract_base_data_arguments(monkeypatch):
    """
    handle_stop_view_by_mach should call extract_base_data with StopExtractor,
    start_time, and end_time. Current behavior does not pass shift.
    """
    raw_df = make_base_stop_view_by_mach_df()
    extract_mock = Mock(return_value=raw_df.copy())
    monkeypatch.setattr(stop_view, "extract_base_data", extract_mock)

    result, *_ = stop_view.handle_stop_view_by_mach(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=0,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        stop_view.StopExtractor,
        "2026-05-01 00:00:00",
        "2026-05-02 00:00:00",
    )


def test_handle_stop_view_by_mach_empty_df(monkeypatch):
    """
    If extract_base_data returns an empty DataFrame, the function should
    return two empty DataFrames immediately.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_view_by_mach_df(),
    )

    outputs = _call_handle_stop_view_by_mach()

    assert len(outputs) == 2
    assert all(output.empty for output in outputs)


def test_handle_stop_view_by_mach_basic_aggregation(monkeypatch):
    """
    Normal case: table rows are grouped by MachID and normalized Style_Code,
    while chart rows are grouped by MachID only. Stop_code and duration should
    not split groups or appear in outputs.
    """
    raw_df = make_base_stop_view_by_mach_df()
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        raw_df,
    )

    result, chart = _call_handle_stop_view_by_mach()
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])
    chart_by_mach = chart.set_index("MachID")
    m1_rows = raw_df[raw_df["MachID"] == "M1"]
    m1_durations = set(m1_rows["Recover_time"] - m1_rows["Stop_time"])

    assert set(m1_rows["Stop_code"]) == {10, 20}
    assert len(m1_durations) == 2
    assert "Stop_code" not in result.columns
    assert "duration" not in result.columns
    assert "Stop_code" not in chart.columns
    assert "duration" not in chart.columns
    assert result_by_mach_style.loc[("M1", "ABC"), "freq"] == 2
    assert result_by_mach_style.loc[("M2", "XYZ"), "freq"] == 1
    assert chart_by_mach.loc["M1", "freq"] == 2
    assert chart_by_mach.loc["M2", "freq"] == 1


def test_handle_stop_view_by_mach_style_code_normalization(monkeypatch):
    """
    Style_Code should be stripped and reduced to its first whitespace token.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_style_normalization_df(),
    )

    result, *_ = _call_handle_stop_view_by_mach()
    result_by_mach_style = result.set_index(["MachID", "Style_Code"])

    assert result_by_mach_style.loc[("M1", "ABC"), "freq"] == 2
    assert result_by_mach_style.loc[("M1", "XYZ"), "freq"] == 1
    assert result_by_mach_style.loc[("M2", "XYZ"), "freq"] == 1


def test_handle_stop_view_by_mach_missing_style_excluded_from_table(monkeypatch):
    """
    Blank, None, and non-string Style_Code values become None and are dropped
    by pandas groupby in the table, and not count in the machine chart.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_missing_style_df(),
    )

    result, chart = _call_handle_stop_view_by_mach()
    chart_by_mach = chart.set_index("MachID")

    assert list(result["MachID"]) == ["M1"]
    assert list(result["Style_Code"]) == ["ABC"]
    assert list(result["freq"]) == [1]
    assert chart_by_mach.loc["M1", "freq"] == 1
    assert "M2" not in chart_by_mach.index


def test_handle_stop_view_by_mach_shift_1_filters_day_shift(monkeypatch):
    """
    shift=1 should keep stops mapped to 07:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_shift_filter_df(),
    )

    result, chart = _call_handle_stop_view_by_mach(shift=1)

    assert set(result["MachID"]) == {"M2", "M3"}
    assert set(result["Style_Code"]) == {"DAY"}
    assert set(chart["MachID"]) == {"M2", "M3"}


def test_handle_stop_view_by_mach_shift_2_filters_night_shift(monkeypatch):
    """
    shift=2 should keep stops mapped to 19:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_shift_filter_df(),
    )

    result, chart = _call_handle_stop_view_by_mach(shift=2)

    assert set(result["MachID"]) == {"M1", "M4", "M5"}
    assert set(result["Style_Code"]) == {"NIGHT"}
    assert set(chart["MachID"]) == {"M1", "M4", "M5"}


def test_handle_stop_view_by_mach_other_shift_includes_all_rows(monkeypatch):
    """
    Current behavior: shift values other than 1 or 2 do not filter rows.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_shift_filter_df(),
    )

    result, chart = _call_handle_stop_view_by_mach(shift=0)

    assert set(result["MachID"]) == {"M1", "M2", "M3", "M4", "M5"}
    assert set(chart["MachID"]) == {"M1", "M2", "M3", "M4", "M5"}


def test_handle_stop_view_by_mach_shift_boundaries(monkeypatch):
    """
    Current boundary behavior:
    07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
    and 19:00:01 is night.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_shift_boundary_df(),
    )

    day_result, day_chart = _call_handle_stop_view_by_mach(shift=1)
    night_result, night_chart = _call_handle_stop_view_by_mach(shift=2)

    assert set(day_result["MachID"]) == {"M2", "M3"}
    assert set(day_chart["MachID"]) == {"M2", "M3"}
    assert set(night_result["MachID"]) == {"M1", "M4"}
    assert set(night_chart["MachID"]) == {"M1", "M4"}


def test_handle_stop_view_by_mach_table_sorting(monkeypatch):
    """
    Table rows should sort by MachID asc, Style_Code asc, and freq desc.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_table_sorting_df(),
    )

    result, *_ = _call_handle_stop_view_by_mach()

    assert list(result["MachID"]) == ["M1", "M1", "M2", "M2"]
    assert list(result["Style_Code"]) == ["AAA", "ZZZ", "AAA", "BBB"]
    assert list(result["freq"]) == [2, 1, 2, 1]
    assert list(result["id"]) == [0, 1, 2, 3]


def test_handle_stop_view_by_mach_chart_sorting(monkeypatch):
    """
    Chart rows should sort by machine frequency descending.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_chart_sorting_df(),
    )

    _, chart = _call_handle_stop_view_by_mach()

    assert list(chart["MachID"]) == ["M1", "M2", "M3"]
    assert list(chart["freq"]) == [3, 2, 1]


def test_handle_stop_view_by_mach_chart_row_cap(monkeypatch):
    """
    Chart output should be capped at 10 rows.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_chart_cap_df(),
    )

    _, chart = _call_handle_stop_view_by_mach()

    assert len(chart) == 10


def test_handle_stop_view_by_mach_filtered_empty_after_shift(monkeypatch):
    """
    If shift filtering removes all rows, post-aggregation outputs should be
    empty and keep their final schemas.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_view_by_mach_filtered_empty_after_shift_df(),
    )

    result, chart = _call_handle_stop_view_by_mach(shift=1)

    assert result.empty
    assert list(result.columns) == EXPECTED_TABLE_COLUMNS
    assert chart.empty
    assert list(chart.columns) == EXPECTED_CHART_COLUMNS
