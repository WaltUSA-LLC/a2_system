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
   - Verify ON_Time_Occupation and Mach_Efficiency calculations and rounding.

8. Comment assignment
   - Verify Mach_Efficiency >= 0.8 is Good and < 0.8 is Low Ef.

9. Machine sorting
   - Verify output rows are sorted by MachID.

10. Invalid Style_Code handling
    - Verify empty or None Style_Code values are excluded without error.

11. Style argument case sensitivity
    - Verify lowercase style argument does not match uppercase normalized rows.
"""


import pytest

import app.services.sku_view as sku_view

from app.tests.mocks.common_mocks import (
    make_call_counting_mocks,
    patch_common_dependencies,
    patch_extract_base_data,
)

from app.tests.mocks.handle_sku_mach_detail_mocks import (
    make_base_sku_mach_detail_df,
    make_empty_sku_mach_detail_df,
    make_sku_mach_detail_df_for_metrics_and_comments,
    make_sku_mach_detail_df_with_invalid_style_code,
    make_sku_mach_detail_df_without_matching_style,
    make_unsorted_sku_mach_detail_df,
)

EXPECTED_COLUMNS = [
        "id",
        "MachID",
        "Shift_Start_Time",
        "Style_Code",
        "MES_prs",
        "NAU_prs",
        "ON_Time",
        "OFF_Time",
        "ON_Time_Occupation",
        "Mach_Efficiency",
        "Comment",
    ]


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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    row = result.iloc[0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"


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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc["M1", "MES_prs"] == 8
    assert result_by_mach.loc["M1", "ON_Time_Occupation"] == pytest.approx(0.8)
    assert result_by_mach.loc["M1", "Mach_Efficiency"] == pytest.approx(0.8)

    assert result_by_mach.loc["M2", "MES_prs"] == 7
    assert result_by_mach.loc["M2", "ON_Time_Occupation"] == pytest.approx(0.5)
    assert result_by_mach.loc["M2", "Mach_Efficiency"] == pytest.approx(0.7)

    assert result_by_mach.loc["M3", "MES_prs"] == 1
    assert result_by_mach.loc["M3", "ON_Time_Occupation"] == pytest.approx(0.333)
    assert result_by_mach.loc["M3", "Mach_Efficiency"] == pytest.approx(0.333)


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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    result_by_mach = result.set_index("MachID")

    assert result_by_mach.loc["M1", "Comment"] == "Good"
    assert result_by_mach.loc["M2", "Comment"] == "Low Ef"
    assert result_by_mach.loc["M3", "Comment"] == "Low Ef"


def test_handle_sku_mach_detail_sorts_by_mach_id(monkeypatch):
    """
    Output rows should be sorted by MachID ascending.
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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert list(result["MachID"]) == ["M1", "M2", "M3"]


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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="ABC",
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["MachID"] == "M3"
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

    result = sku_view.handle_sku_mach_detail(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
        style="abc",
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS
