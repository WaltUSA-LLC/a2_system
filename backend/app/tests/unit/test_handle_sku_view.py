"""
Test cases for handle_sku_view:

1. Output schema
   - Verify the returned DataFrame has the expected columns.

2. Invoked helper functions
   - Verify handle_sku_view calls the expected dependency/helper functions.

3. Shift_Start_Time formatting
   - Verify Shift_Start_Time is converted from pandas Timestamp to string.

4. Normal SKU grouping
   - Verify rows with the same cleaned Style_Code and Shift_Start_Time are grouped correctly.

5. Multiple SKU and multiple shift grouping
   - Verify multiple Style_Code and Shift_Start_Time groups produce multiple output rows.

6. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result immediately.

7. NaN ST_prs handling
   - Verify if any ST_prs in a group is NaN, Efficiency becomes None.

8. Infinite Efficiency handling
   - Verify infinite Efficiency is replaced with None.

9. Invalid Style_Code handling
   - Verify empty or None Style_Code values are dropped by groupby.

10. Filtered-empty result
    - Verify filtering all rows should return an empty result with schema.
"""


from unittest.mock import Mock

import pytest

import app.services.sku_view as sku_view

from app.tests.mocks.common_mocks import (
    make_call_counting_mocks,
    patch_common_dependencies,
    patch_extract_base_data,
)

from app.tests.mocks.handle_sku_view_mocks import (
    make_base_sku_df,
    make_empty_sku_df,
    make_multi_sku_multi_shift_df,
    make_sku_df_with_invalid_style_code,
    make_sku_df_with_nan_st_prs,
    make_sku_df_with_zero_st_prs,
)


EXPECTED_COLUMNS = [
    "id",
    "Style_Code",
    "Shift_Start_Time",
    "Mach_cnt",
    "NAU_prs",
    "MES_prs",
    "ON_Time_Occupation",
    "Efficiency",
]


def _filter_all_shutdown_mach(df):
    return df.iloc[0:0].copy()


def test_handle_sku_view_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_sku_view_calls_invoked_functions(monkeypatch):
    """
    Verify that handle_sku_view calls the invoked helper functions.
    This test focuses on wiring, not calculation correctness.
    """
    raw_df = make_base_sku_df()

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

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert not result.empty
    mocks["distributeWeightForSameMach"].assert_called_once()
    mocks["clean_weight"].assert_called_once()
    mocks["filterShutdownMach"].assert_called_once()
    assert mocks["estimate_mes_output_prs"].call_count == len(raw_df)
    assert mocks["estimate_st_output_prs"].call_count == len(raw_df)


def test_handle_sku_view_shift_start_time_is_string(monkeypatch):
    """
    Shift_Start_Time should be converted from Timestamp to string.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    row = result.iloc[0]

    assert isinstance(row["Shift_Start_Time"], str)
    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"


def test_handle_sku_view_normal_grouping(monkeypatch):
    """
    Normal case:
    two rows are grouped into one SKU group.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["id"] == 0
    assert row["Style_Code"] == "ABC"
    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 8
    assert row["MES_prs"] == 11
    assert row["ON_Time_Occupation"] == pytest.approx(170 / 200)
    assert row["Efficiency"] == pytest.approx(11 / 30)


def test_handle_sku_view_multiple_sku_multiple_shift(monkeypatch):
    """
    Multiple SKU groups should produce multiple output rows.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_multi_sku_multi_shift_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 3

    result_by_style_shift = result.set_index(["Style_Code", "Shift_Start_Time"])

    abc_shift_1 = result_by_style_shift.loc[("ABC", "2026-05-01 07:00:00"), :]
    xyz_shift_1 = result_by_style_shift.loc[("XYZ", "2026-05-01 07:00:00"), :]
    abc_shift_2 = result_by_style_shift.loc[("ABC", "2026-05-01 19:00:00"), :]

    assert abc_shift_1["Mach_cnt"] == 2
    assert abc_shift_1["NAU_prs"] == 6
    assert abc_shift_1["MES_prs"] == 8
    assert abc_shift_1["ON_Time_Occupation"] == pytest.approx(160 / 180)
    assert abc_shift_1["Efficiency"] == pytest.approx(8 / 20)

    assert xyz_shift_1["Mach_cnt"] == 1
    assert xyz_shift_1["NAU_prs"] == 7
    assert xyz_shift_1["MES_prs"] == 4
    assert xyz_shift_1["ON_Time_Occupation"] == pytest.approx(80 / 100)
    assert xyz_shift_1["Efficiency"] == pytest.approx(4 / 10)

    assert abc_shift_2["Mach_cnt"] == 1
    assert abc_shift_2["NAU_prs"] == 3
    assert abc_shift_2["MES_prs"] == 6
    assert abc_shift_2["ON_Time_Occupation"] == pytest.approx(90 / 100)
    assert abc_shift_2["Efficiency"] == pytest.approx(6 / 10)


def test_handle_sku_view_empty_df(monkeypatch):
    """
    If extract_base_data returns empty DataFrame,
    handle_sku_view should immediately return empty DataFrame.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_empty_sku_df(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert result.empty
    mocks["distributeWeightForSameMach"].assert_not_called()
    mocks["clean_weight"].assert_not_called()
    mocks["filterShutdownMach"].assert_not_called()
    mocks["estimate_mes_output_prs"].assert_not_called()
    mocks["estimate_st_output_prs"].assert_not_called()


def test_handle_sku_view_nan_st_prs_efficiency_becomes_none(monkeypatch):
    """
    If one ST_prs in a group is NaN,
    group-level ST_prs becomes NaN.

    Then Efficiency becomes NaN and is replaced with None.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_df_with_nan_st_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Style_Code"] == "XYZ"
    assert row["MES_prs"] == 8
    assert row["Efficiency"] is None


def test_handle_sku_view_infinite_efficiency_becomes_none(monkeypatch):
    """
    If ST_prs group sum is 0 and MES_prs > 0,
    Efficiency becomes inf.
    The final replace should convert inf to None.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_df_with_zero_st_prs(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["Style_Code"] == "AAA"
    assert row["MES_prs"] == 10
    assert row["Efficiency"] is None


def test_handle_sku_view_invalid_style_code_is_dropped(monkeypatch):
    """
    Style_Code values like "" and None become None after cleaning.
    Pandas groupby drops NA groups by default,
    so the result should be empty.
    """

    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_df_with_invalid_style_code(),
    )

    mocks = make_call_counting_mocks()
    patch_common_dependencies(
        monkeypatch,
        sku_view,
        mocks,
    )

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert result.empty


def test_handle_sku_view_filtered_empty_returns_empty_with_schema(monkeypatch):
    """
    If filterShutdownMach removes all rows, handle_sku_view should return an
    empty DataFrame with the final schema.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_df(),
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

    result = sku_view.handle_sku_view(
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
        shift=1,
    )

    assert result.empty
