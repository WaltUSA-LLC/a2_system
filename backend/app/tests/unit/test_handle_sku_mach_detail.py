"""
Test cases for handle_sku_mach_detail:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Invoked helper functions
   - Verify handle_sku_mach_detail calls the expected dependency/helper
     functions.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

4. Shift_Start_Time formatting
   - Verify Shift_Start_Time is converted from pandas Timestamp to string.

5. Style filtering
   - Verify style filtering uses Style_Code without size/color suffix.

6. No matching style
   - Verify no matching style returns an empty result with the final schema.

7. Metric calculations
   - Verify Discard_prs pass-through, ON_Time_Occupation, and
     Mach_Efficiency calculations and rounding.

8. Comment assignment
   - Verify Mach_Efficiency >= 0.8 is Good and < 0.8 is Low Ef.

9. Machine sorting
   - Verify output rows are sorted by LineID and then MachID.

10. Invalid Style_Code handling
    - Verify empty or None Style_Code values are excluded without error.

11. Style argument case sensitivity
    - Verify lowercase style argument does not match uppercase normalized rows.

12. Filtered-empty result
    - Verify filtering all rows should return an empty result with schema.

13. Shutdown machine filtering
    - Verify filtered rows do not appear in Discard_prs output.

14. NaN Discard_prs handling
    - Verify NaN Discard_prs is converted to None.

15. Zero Discard_percent denominator behavior
    - Verify zero NAU_prs and zero Discard_prs becomes None.
"""


from unittest.mock import Mock

import pytest

import app.services.sku_view as sku_view

from app.tests.mocks.common_mocks import (
    make_call_counting_mocks,
    patch_common_dependencies,
    patch_determine_mach_line,
    patch_extract_base_data,
    patch_merge_pqc_to_mach_dialog,
)

from app.tests.mocks.handle_sku_mach_detail_mocks import (
    make_base_sku_mach_detail_df,
    make_empty_sku_mach_detail_df,
    make_sku_mach_detail_df_for_metrics_and_comments,
    make_sku_mach_detail_df_with_invalid_style_code,
    make_sku_mach_detail_df_with_nan_discard_prs,
    make_sku_mach_detail_df_with_zero_discard_denominator,
    make_sku_mach_detail_df_without_matching_style,
    make_unsorted_sku_mach_detail_df,
)

EXPECTED_COLUMNS = [
        "id",
        "LineID",
        "MachID",
        "Shift_Start_Time",
        "Style_Code",
        "MES_prs",
        "NAU_prs",
        "Discard_prs",
        "Discard_percent",
        "ON_Time",
        "OFF_Time",
        "ON_Time_Occupation",
        "Mach_Efficiency",
        "Comment",
    ]


def _filter_all_shutdown_mach(df):
    return df.iloc[0:0].copy()


def _filter_m2_shutdown_mach(df):
    return df[df["MachID"] != 2].copy()


def _assert_merge_pqc_to_mach_dialog_called_once(mock, start_time, shift):
    mock.assert_called_once()
    _, actual_start_time, actual_shift = mock.call_args.args
    assert actual_start_time == start_time
    assert actual_shift == shift


def test_handle_sku_mach_detail_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_sku_mach_detail_calls_invoked_functions(monkeypatch):
    """
    Verify that handle_sku_mach_detail calls the invoked helper functions.
    This test focuses on wiring and filter order, not calculation correctness.
    """
    raw_df = make_base_sku_mach_detail_df()

    patch_extract_base_data(
        monkeypatch,
        sku_view,
        raw_df,
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    pqc_merge_mock = patch_merge_pqc_to_mach_dialog(
        monkeypatch,
        sku_view,
    )
    determine_mach_line_mock = patch_determine_mach_line(
        monkeypatch,
        sku_view,
    )

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 2
    mocks["distributeWeightForSameMach"].assert_called_once()
    mocks["clean_weight"].assert_called_once()
    mocks["filterShutdownMach"].assert_called_once()
    assert mocks["estimate_mes_output_prs"].call_count == len(raw_df)
    assert mocks["estimate_st_output_prs"].call_count == len(result)
    assert determine_mach_line_mock.call_count == len(result)
    assert [
        call.args[0]
        for call in determine_mach_line_mock.call_args_list
    ] == [2, 1]
    _assert_merge_pqc_to_mach_dialog_called_once(
        pqc_merge_mock,
        "2026-05-01 00:00:00",
        1,
    )


def test_handle_sku_mach_detail_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_sku_mach_detail should immediately return empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_empty_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    pqc_merge_mock = patch_merge_pqc_to_mach_dialog(
        monkeypatch,
        sku_view,
    )

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert result.empty
    mocks["distributeWeightForSameMach"].assert_not_called()
    mocks["clean_weight"].assert_not_called()
    mocks["filterShutdownMach"].assert_not_called()
    mocks["estimate_mes_output_prs"].assert_not_called()
    mocks["estimate_st_output_prs"].assert_not_called()
    pqc_merge_mock.assert_not_called()


def test_handle_sku_mach_detail_shift_start_time_is_string(monkeypatch):
    """
    Shift_Start_Time should be converted from Timestamp to string.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    row = result.iloc[0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"


def test_handle_sku_mach_detail_filters_by_style_without_size(monkeypatch):
    """
    Style filtering should use the first token of Style_Code after stripping
    and uppercasing, while final Style_Code keeps the full cleaned value.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 2
    assert set(result["Style_Code"]) == {"ABC RED", "ABC BLUE"}
    assert "XYZ BLACK" not in set(result["Style_Code"])


def test_handle_sku_mach_detail_no_matching_style_returns_empty_with_schema(
    monkeypatch,
):
    """
    If no row matches style, the final result should be empty but keep the
    final schema.
    """
    raw_df = make_sku_mach_detail_df_without_matching_style()
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        raw_df,
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS
    assert mocks["estimate_mes_output_prs"].call_count == len(raw_df)
    assert mocks["estimate_st_output_prs"].call_count < len(raw_df)


def test_handle_sku_mach_detail_calculates_metrics(monkeypatch):
    """
    Verify machine-level ON time occupation and efficiency calculations.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_for_metrics_and_comments(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc[1, "MES_prs"] == 8
    assert result_by_mach.loc[1, "Discard_prs"] == 1
    assert result_by_mach.loc[1, "Discard_percent"] == pytest.approx(0.143)
    assert result_by_mach.loc[1, "ON_Time_Occupation"] == pytest.approx(0.8)
    assert result_by_mach.loc[1, "Mach_Efficiency"] == pytest.approx(0.8)

    assert result_by_mach.loc[2, "MES_prs"] == 7
    assert result_by_mach.loc[2, "Discard_prs"] == 2
    assert result_by_mach.loc[2, "Discard_percent"] == pytest.approx(0.286)
    assert result_by_mach.loc[2, "ON_Time_Occupation"] == pytest.approx(0.5)
    assert result_by_mach.loc[2, "Mach_Efficiency"] == pytest.approx(0.7)

    assert result_by_mach.loc[3, "MES_prs"] == 1
    assert result_by_mach.loc[3, "Discard_prs"] == 3
    assert result_by_mach.loc[3, "Discard_percent"] == pytest.approx(0.75)
    assert result_by_mach.loc[3, "ON_Time_Occupation"] == pytest.approx(0.333)
    assert result_by_mach.loc[3, "Mach_Efficiency"] == pytest.approx(0.333)


def test_handle_sku_mach_detail_comment_good_and_low_eff(monkeypatch):
    """
    Machines with efficiency >= 0.8 should be Good.
    Machines with efficiency < 0.8 should be Low Ef.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_for_metrics_and_comments(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc[1, "Comment"] == "Good"
    assert result_by_mach.loc[2, "Comment"] == "Low Ef"
    assert result_by_mach.loc[3, "Comment"] == "Low Ef"


def test_handle_sku_mach_detail_sorts_by_line_then_mach_id(monkeypatch):
    """
    Output rows should be sorted by LineID and then MachID ascending.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_unsorted_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert list(result["MachID"]) == [1, 3, 2]
    assert list(result["Discard_prs"]) == [2, 1, 3]
    assert list(result["Discard_percent"]) == pytest.approx([0.333, 0.143, 0.375])


def test_handle_sku_mach_detail_filter_shutdown_mach_affects_rows(
    monkeypatch,
):
    """
    filterShutdownMach should remove rows before Discard_prs output and
    estimator calls are calculated.
    """
    raw_df = make_base_sku_mach_detail_df()

    patch_extract_base_data(
        monkeypatch,
        sku_view,
        raw_df,
    )

    mocks = make_call_counting_mocks()
    mocks["filterShutdownMach"] = Mock(
        side_effect=_filter_m2_shutdown_mach
    )
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 1
    assert list(result["MachID"]) == [1]
    assert list(result["Discard_prs"]) == [2]
    assert list(result["Discard_percent"]) == pytest.approx([0.333])
    assert mocks["estimate_mes_output_prs"].call_count == 2
    assert mocks["estimate_st_output_prs"].call_count == 1


def test_handle_sku_mach_detail_invalid_style_code_is_excluded(monkeypatch):
    """
    Style_Code values like "" and None should become None after cleaning,
    so they should not match the requested style.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_with_invalid_style_code(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["MachID"] == 3
    assert row["Style_Code"] == "ABC RED"


def test_handle_sku_mach_detail_style_argument_is_case_sensitive(monkeypatch):
    """
    Current behavior: Style_Code is normalized to uppercase, but style argument
    is not. A lowercase style argument should not match.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="abc",
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_sku_mach_detail_filtered_empty_returns_empty_with_schema(
    monkeypatch,
):
    """
    If filterShutdownMach removes all rows, handle_sku_mach_detail should
    return an empty DataFrame with the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )

    mocks = make_call_counting_mocks()
    mocks["filterShutdownMach"] = Mock(
        side_effect=_filter_all_shutdown_mach
    )
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    pqc_merge_mock = patch_merge_pqc_to_mach_dialog(
        monkeypatch,
        sku_view,
    )

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert result.empty
    pqc_merge_mock.assert_not_called()


def test_handle_sku_mach_detail_nan_discard_prs_becomes_none(monkeypatch):
    """
    If Discard_prs is NaN, the final null conversion should convert it to None.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_with_nan_discard_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    row = result.iloc[0]

    assert row["Discard_prs"] is None
    assert row["Discard_percent"] is None


def test_handle_sku_mach_detail_zero_discard_denominator_becomes_none(
    monkeypatch,
):
    """
    If NAU_prs + Discard_prs is 0, Discard_percent becomes NaN.
    The final replace should convert NaN to None.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_with_zero_discard_denominator(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )
    patch_merge_pqc_to_mach_dialog(monkeypatch, sku_view)

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["NAU_prs"] == 0
    assert row["Discard_prs"] == 0
    assert row["Discard_percent"] is None
