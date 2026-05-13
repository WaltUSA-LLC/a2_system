"""
Test cases for distributeWeightForSameMach:

1. Single-row group
   - Verify a machine/shift group with one row keeps its original Weight.

2. Same machine and same shift
   - Verify duplicated machine-shift Weight is distributed by ON_Time ratio.

3. Different machines in the same shift
   - Verify each MachID group is distributed independently.

4. Same machine in different shifts
   - Verify each Shift_Start_Time group is distributed independently.

5. Zero total ON_Time
   - Verify Weight is divided evenly by group size when ON_Time sum is 0.

6. Mixed zero and nonzero ON_Time
   - Verify rows with 0 ON_Time receive 0 Weight when group ON_Time is positive.

7. Input immutability
   - Verify the original DataFrame is not mutated.

8. Non-Weight column preservation
   - Verify only Weight is changed and other columns remain unchanged.

9. Unexpected differing weights
   - Document current behavior if same machine/shift rows have different
     Weight values, even though valid source data should duplicate Weight.
"""


import pandas as pd
import pytest

from app.services.utils import distributeWeightForSameMach
from app.tests.mocks.handle_distributeWeightForSameMach_mocks import (
    make_different_mach_same_shift_df,
    make_mixed_zero_and_nonzero_on_time_df,
    make_same_mach_different_shift_df,
    make_same_mach_df_with_extra_columns,
    make_same_mach_df_with_unexpected_different_weights,
    make_same_mach_same_shift_df,
    make_single_row_same_mach_df,
    make_zero_on_time_same_mach_df,
)


def test_distribute_weight_single_row_group_remains_unchanged():
    """
    A group with only one machine/shift row should keep the original Weight.
    """
    df = make_single_row_same_mach_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([100])


def test_distribute_weight_same_mach_same_shift_by_on_time_ratio():
    """
    Duplicated Weight for the same machine/shift should be split by ON_Time.
    """
    df = make_same_mach_same_shift_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([30, 70])
    assert result["Weight"].sum() == pytest.approx(100)


def test_distribute_weight_different_machines_are_independent():
    """
    Rows from different MachID groups should not affect each other's Weight.
    """
    df = make_different_mach_same_shift_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([30, 70, 40, 160])

    result_by_mach = result.groupby("MachID")["Weight"].sum()
    assert result_by_mach.loc["M1"] == pytest.approx(100)
    assert result_by_mach.loc["M2"] == pytest.approx(200)


def test_distribute_weight_same_mach_different_shifts_are_independent():
    """
    Rows from different Shift_Start_Time groups should be distributed separately.
    """
    df = make_same_mach_different_shift_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([25, 75, 120, 180])

    result_by_shift = result.groupby("Shift_Start_Time")["Weight"].sum()
    assert result_by_shift.loc[pd.Timestamp("2026-05-01 08:00:00")] == (
        pytest.approx(100)
    )
    assert result_by_shift.loc[pd.Timestamp("2026-05-01 20:00:00")] == (
        pytest.approx(300)
    )


def test_distribute_weight_zero_total_on_time_divides_evenly():
    """
    If a machine/shift group has no ON_Time, divide Weight by row count.
    """
    df = make_zero_on_time_same_mach_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([50, 50])
    assert result["Weight"].sum() == pytest.approx(100)


def test_distribute_weight_mixed_zero_and_nonzero_on_time_uses_ratio():
    """
    If group ON_Time is positive, use ON_Time ratio even when one row is 0.
    """
    df = make_mixed_zero_and_nonzero_on_time_df()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([0, 100])
    assert result["Weight"].sum() == pytest.approx(100)


def test_distribute_weight_does_not_mutate_original_df():
    """
    distributeWeightForSameMach should return a copy and leave input unchanged.
    """
    df = make_same_mach_same_shift_df()
    original_df = df.copy(deep=True)

    distributeWeightForSameMach(df)

    pd.testing.assert_frame_equal(df, original_df)


def test_distribute_weight_preserves_non_weight_columns():
    """
    Only Weight should be recalculated; all other columns should be preserved.
    """
    df = make_same_mach_df_with_extra_columns()

    result = distributeWeightForSameMach(df)

    non_weight_columns = [column for column in df.columns if column != "Weight"]
    pd.testing.assert_frame_equal(
        result[non_weight_columns],
        df[non_weight_columns],
    )
    assert result["Weight"].tolist() == pytest.approx([40, 60])


def test_distribute_weight_documents_unexpected_different_weight_behavior():
    """
    Weight should normally be duplicated for the same machine and shift.
    If unexpected differing weights appear, current behavior applies each
    row's own weight before allocation.
    """
    df = make_same_mach_df_with_unexpected_different_weights()

    result = distributeWeightForSameMach(df)

    assert result["Weight"].tolist() == pytest.approx([30, 140])
    assert result["Weight"].sum() == pytest.approx(170)
