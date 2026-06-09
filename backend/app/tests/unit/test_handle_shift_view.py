"""
Test cases for handle_shift_view:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Invoked helper functions
   - Verify handle_shift_view calls the expected dependency/helper functions.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

4. Single-shift aggregation
   - Verify machine count, throughput totals, efficiency, and time occupation.

5. Multiple-shift aggregation
   - Verify multiple Shift_Start_Time groups produce multiple output rows.

6. Duplicate machine count
   - Verify repeated MachID values are counted once in Mach_cnt.

7. Shutdown machine filtering
   - Verify filterShutdownMach affects totals and estimator call counts.

8. Infinite efficiency handling
   - Verify infinite eff is replaced with None.

9. NaN value handling
    - Verify NaN Time_Occupation is replaced with None.

10. Filtered-empty result
    - Verify filtering all rows should return an empty result.

11. Current NaN ST_prs behavior
    - Verify pandas groupby sum skips NaN ST_prs values in current code.

12. Current NaN Discard_prs behavior
    - Verify pandas groupby sum skips NaN Discard_prs values in current code.

13. Zero Discard_percent denominator behavior
    - Verify zero NAU_prs and zero Discard_prs becomes None.
"""


from unittest.mock import Mock

import pandas as pd
import pytest

import app.services.shift_view as shift_view

from app.tests.mocks.common_mocks import (
    make_call_counting_mocks,
    patch_common_dependencies,
    patch_extract_base_data,
    patch_merge_staff_info_to_view,
    patch_merge_pqc_to_shift_view,
)

from app.tests.mocks.handle_shift_view_mocks import (
    make_base_shift_df,
    make_empty_shift_df,
    make_multi_shift_df,
    make_shift_df_for_filter_shutdown,
    make_shift_df_that_filters_to_empty,
    make_shift_df_with_duplicate_mach,
    make_shift_df_with_nan_discard_prs,
    make_shift_df_with_nan_st_prs,
    make_shift_df_with_zero_discard_denominator,
    make_shift_df_with_zero_st_prs,
    make_shift_df_with_zero_time,
)

EXPECTED_COLUMNS = [
    "id",
    "Shift_Start_Time",
    "Mach_cnt",
    "NAU_prs",
    "MES_prs",
    "Discard_prs",
    "Discard_percent",
    "ST_prs",
    "eff",
    "Time_Occupation",
]


def _filter_marked_shutdown_mach(df):
    filtered_df = df[~df["Should_Filter"]].copy()
    return filtered_df.drop(columns=["Should_Filter"])


def _assert_merge_staff_info_called_once(mock, start_time, end_time):
    mock.assert_called_once()
    _, actual_start_time, actual_end_time = mock.call_args.args
    assert actual_start_time == start_time
    assert actual_end_time == end_time


def _assert_merge_pqc_into_shift_view_called_once(mock, start_time, end_time, shift):
    mock.assert_called_once()
    _, actual_start_time, actual_end_time, actual_shift = mock.call_args.args
    assert actual_start_time == start_time
    assert actual_end_time == end_time
    assert actual_shift == shift


def test_handle_shift_view_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_staff_info_to_view(
        monkeypatch,
        shift_view,
    )

    patch_merge_pqc_to_shift_view(
        monkeypatch,
        shift_view,
    )

    result = shift_view.handle_shift_view(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_shift_view_calls_invoked_functions(monkeypatch):
    """
    Verify that handle_shift_view calls the invoked helper functions.
    This test focuses on wiring, not calculation correctness.
    """
    raw_df = make_base_shift_df()

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
    staff_merge_mock = patch_merge_staff_info_to_view(
        monkeypatch,
        shift_view,
    )
    pqc_merge_mock = patch_merge_pqc_to_shift_view(
        monkeypatch,
        shift_view,
    )

    result = shift_view.handle_shift_view(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert not result.empty
    mocks["distributeWeightForSameMach"].assert_called_once()
    mocks["clean_weight"].assert_called_once()
    mocks["filterShutdownMach"].assert_called_once()
    assert mocks["estimate_mes_output_prs"].call_count == len(raw_df)
    assert mocks["estimate_st_output_prs"].call_count == len(raw_df)
    _assert_merge_staff_info_called_once(
        staff_merge_mock,
        "2026-05-01",
        "2026-05-02",
    )
    _assert_merge_pqc_into_shift_view_called_once(
        pqc_merge_mock,
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_handle_shift_view_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_shift_view should immediately return empty DataFrame.
    """
    mock_extract = patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_empty_shift_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    staff_merge_mock = patch_merge_staff_info_to_view(
        monkeypatch,
        shift_view,
    )
    pqc_merge_mock = patch_merge_pqc_to_shift_view(
        monkeypatch,
        shift_view,
    )

    result = shift_view.handle_shift_view(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result.empty
    mock_extract.assert_called()
    assert mock_extract.call_count == 1
    mocks["distributeWeightForSameMach"].assert_not_called()
    mocks["clean_weight"].assert_not_called()
    mocks["filterShutdownMach"].assert_not_called()
    mocks["estimate_mes_output_prs"].assert_not_called()
    mocks["estimate_st_output_prs"].assert_not_called()
    pqc_merge_mock.assert_not_called()
    staff_merge_mock.assert_not_called()


def test_handle_shift_view_single_shift_aggregation(monkeypatch):
    """
    Normal case:
    three machine rows are grouped into one shift group.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["id"] == 0
    assert row["Shift_Start_Time"] == pd.Timestamp("2026-05-01 07:00:00")
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 8
    assert row["MES_prs"] == 11
    assert row["Discard_prs"] == 6
    assert row["Discard_percent"] == pytest.approx(0.429)
    assert row["ST_prs"] == 30
    assert row["eff"] == pytest.approx(0.367)
    assert row["Time_Occupation"] == pytest.approx(170/200)


def test_handle_shift_view_multiple_shift_aggregation(monkeypatch):
    """
    Multiple shift groups should produce multiple output rows.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_multi_shift_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 2

    result_by_shift = result.set_index("Shift_Start_Time")

    shift_1 = result_by_shift.loc[pd.Timestamp("2026-05-01 07:00:00"), :]
    shift_2 = result_by_shift.loc[pd.Timestamp("2026-05-01 19:00:00"), :]

    assert shift_1["Mach_cnt"] == 2
    assert shift_1["NAU_prs"] == 6
    assert shift_1["MES_prs"] == 8
    assert shift_1["Discard_prs"] == 3
    assert shift_1["Discard_percent"] == pytest.approx(0.333)
    assert shift_1["ST_prs"] == 20
    assert shift_1["eff"] == pytest.approx(0.4)
    assert shift_1["Time_Occupation"] == pytest.approx(0.889)
    assert shift_2["Mach_cnt"] == 2
    assert shift_2["NAU_prs"] == 10
    assert shift_2["MES_prs"] == 10
    assert shift_2["Discard_prs"] == 7
    assert shift_2["Discard_percent"] == pytest.approx(0.412)
    assert shift_2["ST_prs"] == 30
    assert shift_2["eff"] == pytest.approx(0.333)
    assert shift_2["Time_Occupation"] == pytest.approx(0.75)


def test_handle_shift_view_duplicate_mach_counted_once(monkeypatch):
    """
    Repeated MachID values in the same shift should be counted once.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_duplicate_mach(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 12
    assert row["MES_prs"] == 18
    assert row["Discard_prs"] == 6
    assert row["Discard_percent"] == pytest.approx(0.333)
    assert row["ST_prs"] == 30


def test_handle_shift_view_filter_shutdown_mach_affects_aggregation(
    monkeypatch,
):
    """
    filterShutdownMach should remove rows before throughput and efficiency
    calculations are applied.
    """
    raw_df = make_shift_df_for_filter_shutdown()

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
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 9
    assert row["MES_prs"] == 12
    assert row["Discard_prs"] == 4
    assert row["Discard_percent"] == pytest.approx(0.308)
    assert row["ST_prs"] == 30
    assert row["eff"] == pytest.approx(0.4)
    assert row["Time_Occupation"] == pytest.approx(0.8)
    assert mocks["estimate_mes_output_prs"].call_count == 2
    assert mocks["estimate_st_output_prs"].call_count == 2


def test_handle_shift_view_infinite_efficiency_becomes_none(monkeypatch):
    """
    If ST_prs group sum is 0 and MES_prs > 0,
    eff becomes inf and final replace should convert it to None.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_zero_st_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["MES_prs"] == 10
    assert row["ST_prs"] == 0
    assert row["eff"] is None


def test_handle_shift_view_nan_time_occupation_becomes_none(monkeypatch):
    """
    If ON_Time + OFF_Time is 0, Time_Occupation becomes NaN.
    The final replace should convert NaN to None.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_zero_time(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Time_Occupation"] is None
    assert row["eff"] == pytest.approx(0.5)


def test_handle_shift_view_filtered_empty_returns_empty(
    monkeypatch,
):
    """
    If filterShutdownMach removes all rows, handle_shift_view should return an
    empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_that_filters_to_empty(),
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
    staff_merge_mock = patch_merge_staff_info_to_view(
        monkeypatch,
        shift_view,
    )
    pqc_merge_mock = patch_merge_pqc_to_shift_view(
        monkeypatch,
        shift_view,
    )

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert result.empty
    pqc_merge_mock.assert_not_called()
    staff_merge_mock.assert_not_called()


def test_handle_shift_view_nan_st_prs_current_behavior(monkeypatch):
    """
    Current behavior:
    pandas groupby sum skips NaN ST_prs values, so the group ST_prs is based
    on the non-NaN rows.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_nan_st_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["NAU_prs"] == 6
    assert row["MES_prs"] == 8
    assert row["ST_prs"] == 10
    assert row["eff"] == pytest.approx(0.8)
    assert row["Time_Occupation"] == pytest.approx(0.889)


def test_handle_shift_view_nan_discard_prs_current_behavior(monkeypatch):
    """
    Current behavior:
    pandas groupby sum skips NaN Discard_prs values, so the group Discard_prs
    is based on the non-NaN rows.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_nan_discard_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Discard_prs"] == 1
    assert row["Discard_percent"] == pytest.approx(0.143)


def test_handle_shift_view_zero_discard_denominator_becomes_none(monkeypatch):
    """
    If NAU_prs + Discard_prs is 0, Discard_percent becomes NaN.
    The final replace should convert NaN to None.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_df_with_zero_discard_denominator(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        shift_view,
        mocks,
    )
    patch_merge_pqc_to_shift_view(monkeypatch, shift_view)
    patch_merge_staff_info_to_view(monkeypatch, shift_view)

    result = shift_view.handle_shift_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["NAU_prs"] == 0
    assert row["Discard_prs"] == 0
    assert row["Discard_percent"] is None
