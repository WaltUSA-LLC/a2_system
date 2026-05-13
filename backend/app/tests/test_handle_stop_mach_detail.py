"""
Test cases for handle_stop_mach_detail:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start_time, and end_time.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

4. Machine and style filtering
   - Verify only matching MachID and normalized Style_Code rows remain.

5. Style code normalization
   - Verify Style_Code is stripped and reduced to its first token.

6. Invalid Style_Code handling
   - Verify empty, None, and non-string Style_Code values are excluded.

7. Description trimming
   - Verify Description is stripped.

8. Shift 1 filtering
   - Verify only day-shift rows are included.

9. Shift 2 filtering
   - Verify only night-shift rows are included.

10. All-shifts behavior
    - Verify shift values other than 1 and 2 include all shifts.

11. Shift boundary behavior
    - Verify 07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
      and 19:00:01 is night.

12. Timestamp formatting
    - Verify Stop_time and Recover_time are converted to strings.

13. Duration calculation
    - Verify duration is Recover_time minus Stop_time.

14. Sorting
    - Verify rows sort by Start_Shift_Time asc and duration desc.

15. Null conversion
    - Verify pandas null values are converted to Python None.

16. Filtered-empty result
    - Verify filtering all rows returns an empty result with schema.
"""


from unittest.mock import Mock

import pandas as pd

import app.services.stop_view as stop_view

from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.handle_stop_mach_detail_mocks import (
    make_base_stop_mach_detail_df,
    make_empty_stop_mach_detail_df,
    make_stop_mach_detail_filtered_empty_after_shift_df,
    make_stop_mach_detail_missing_style_df,
    make_stop_mach_detail_no_matching_mach_style_df,
    make_stop_mach_detail_null_conversion_df,
    make_stop_mach_detail_shift_boundary_df,
    make_stop_mach_detail_shift_filter_df,
    make_stop_mach_detail_sorting_df,
    make_stop_mach_detail_style_normalization_df,
)


EXPECTED_COLUMNS = [
    "id",
    "Stop_code",
    "Description",
    "MachID",
    "Style_Code",
    "Stop_time",
    "Recover_time",
    "duration",
    "Start_Shift_Time",
]


def _call_handle_stop_mach_detail(shift=0, mach=1, style="ABC"):
    return stop_view.handle_stop_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=shift,
        mach=mach,
        style=style,
    )


def test_handle_stop_mach_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail()

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_stop_mach_detail_extract_base_data_arguments(monkeypatch):
    """
    handle_stop_mach_detail should call extract_base_data with StopExtractor,
    start_time, and end_time. Current behavior does not pass shift, mach, or
    style.
    """
    raw_df = make_base_stop_mach_detail_df()
    extract_mock = Mock(return_value=raw_df.copy())
    monkeypatch.setattr(stop_view, "extract_base_data", extract_mock)

    result = stop_view.handle_stop_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        mach=1,
        style="ABC",
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        stop_view.StopExtractor,
        "2026-05-01 00:00:00",
        "2026-05-02 00:00:00"
    )


def test_handle_stop_mach_detail_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_stop_mach_detail should immediately return empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail()

    assert result.empty


def test_handle_stop_mach_detail_filters_by_mach_and_style(monkeypatch):
    """
    Normal case:
    only rows matching MachID and normalized Style_Code should remain.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert len(result) == 2
    assert set(result["MachID"]) == {1}
    assert set(result["Style_Code"]) == {"ABC"}
    assert set(result["Description"]) == {"Jam", "Low Air"}


def test_handle_stop_mach_detail_style_code_normalization(monkeypatch):
    """
    Style_Code should be stripped and reduced to its first whitespace token.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_style_normalization_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert len(result) == 2
    assert set(result["Style_Code"]) == {"ABC"}
    assert set(result["Description"]) == {"First ABC", "Second ABC"}


def test_handle_stop_mach_detail_invalid_style_code_is_excluded(monkeypatch):
    """
    Style_Code values like "", whitespace, None, and non-string values become
    None after cleaning and should not match the requested style.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_missing_style_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Style_Code"] == "ABC"
    assert row["Description"] == "Valid Style"


def test_handle_stop_mach_detail_trims_description(monkeypatch):
    """
    Description should be stripped in the final result.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert " Jam " not in set(result["Description"])
    assert "Jam" in set(result["Description"])


def test_handle_stop_mach_detail_shift_1_filters_day_shift(monkeypatch):
    """
    shift=1 should keep stops mapped to 07:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_shift_filter_df(),
    )

    result = _call_handle_stop_mach_detail(shift=1, mach=1, style="ABC")

    assert set(result["Description"]) == {"Day Start", "Day End"}
    assert set(result["Start_Shift_Time"]) == {"2026-05-01 07:00:00"}


def test_handle_stop_mach_detail_shift_2_filters_night_shift(monkeypatch):
    """
    shift=2 should keep stops mapped to 19:00:00 shift start.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_shift_filter_df(),
    )

    result = _call_handle_stop_mach_detail(shift=2, mach=1, style="ABC")

    assert set(result["Description"]) == {
        "Night Previous",
        "Night Start",
        "Night End",
    }
    assert set(result["Start_Shift_Time"]) == {
        "2026-04-30 19:00:00",
        "2026-05-01 19:00:00",
    }


def test_handle_stop_mach_detail_other_shift_includes_all_shifts(monkeypatch):
    """
    Current behavior: shift values other than 1 or 2 do not filter rows by
    shift.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_shift_filter_df(),
    )

    result = _call_handle_stop_mach_detail(shift=0, mach=1, style="ABC")

    assert set(result["Description"]) == {
        "Night Previous",
        "Day Start",
        "Day End",
        "Night Start",
        "Night End",
    }


def test_handle_stop_mach_detail_shift_boundaries(monkeypatch):
    """
    Current boundary behavior:
    07:00:00 is night, 07:00:01 is day, 19:00:00 is day,
    and 19:00:01 is night.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_shift_boundary_df(),
    )

    day_result = _call_handle_stop_mach_detail(
        shift=1,
        mach=1,
        style="ABC",
    )
    night_result = _call_handle_stop_mach_detail(
        shift=2,
        mach=1,
        style="ABC",
    )

    assert set(day_result["Description"]) == {
        "Day After Seven",
        "Seven PM Included Day",
    }
    assert set(night_result["Description"]) == {
        "Seven AM Included Night",
        "Night After Seven PM",
    }


def test_handle_stop_mach_detail_formats_timestamps_as_strings(monkeypatch):
    """
    Stop_time and Recover_time should be converted from Timestamp to string.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")
    row = result.iloc[0]

    assert isinstance(row["Stop_time"], str)
    assert isinstance(row["Recover_time"], str)
    assert row["Stop_time"] == "2026-05-01 09:00:00"
    assert row["Recover_time"] == "2026-05-01 09:15:00"


def test_handle_stop_mach_detail_calculates_duration(monkeypatch):
    """
    duration should be Recover_time minus Stop_time.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")
    result_by_stop_code = result.set_index("Stop_code")

    assert result_by_stop_code.loc[10, "duration"] == pd.Timedelta(minutes=5)
    assert result_by_stop_code.loc[20, "duration"] == pd.Timedelta(minutes=15)


def test_handle_stop_mach_detail_sorting(monkeypatch):
    """
    Rows should sort by Start_Shift_Time ascending and duration descending.
    reset_index keeps the original row index as id.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_sorting_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert list(result["Description"]) == [
        "Day Long",
        "Day Short",
        "Night Long",
        "Night Short",
    ]
    assert list(result["id"]) == [2, 0, 1, 3]


def test_handle_stop_mach_detail_null_values_become_none(monkeypatch):
    """
    Final null replacement in description should convert pandas null values to Python None.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_null_conversion_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")
    row = result[result["Stop_code"] == 10].iloc[0]

    assert row["Description"] is None
    assert row["Optional_Note"] is None


def test_handle_stop_mach_detail_filtered_empty_returns_schema(monkeypatch):
    """
    If filtering removes all rows after extraction, the result should be empty
    and keep the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_filtered_empty_after_shift_df(),
    )

    result = _call_handle_stop_mach_detail(shift=1, mach=1, style="ABC")

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_stop_mach_detail_no_matching_mach_style_returns_schema(
    monkeypatch,
):
    """
    If machine and style filtering removes all rows, the result should be
    empty and keep the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_stop_mach_detail_no_matching_mach_style_df(),
    )

    result = _call_handle_stop_mach_detail(mach=1, style="ABC")

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS
