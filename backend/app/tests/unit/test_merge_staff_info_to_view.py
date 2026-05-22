"""
Test cases for merge_staff_info_to_view:

1. Matching staff join
   - Verify staff columns are merged into matching Shift_Start_Time rows.

2. Unmatched staff schedule
   - Verify unmatched shift rows are preserved with null role values.

3. Empty staff schedule
   - Verify an empty staff schedule preserves rows with null role values.

4. Shift_Start_Time conversion
   - Verify string and Timestamp values are handled and formatted as strings.

5. Staff lookup arguments
   - Verify get_staff_schedule_table receives start_time and end_time.
"""

import pandas as pd

import app.services.staff_info as staff_info

from app.tests.mocks.common_mocks import patch_get_staff_schedule_table
from app.tests.mocks.staff_schedule_mocks import (
    STAFF_ROLE_COLUMNS,
    make_base_staff_schedule_df,
    make_empty_staff_schedule_df,
    make_multi_staff_schedule_df,
    make_unmatched_staff_schedule_df,
)


def _make_base_view_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [
                0,
            ],
            "Shift_Start_Time": [
                pd.Timestamp("2026-05-01 07:00:00"),
            ],
            "Mach_cnt": [
                2,
            ],
            "MES_prs": [
                10,
            ],
        }
    )


def test_merge_staff_info_to_view_matching_staff_join(monkeypatch):
    """
    Staff columns should be merged into matching Shift_Start_Time rows.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    result = staff_info.merge_staff_info_to_view(
        _make_base_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
    )

    row = result.iloc[0]

    assert "ShiftStartTime" not in result.columns
    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert row["Mach_cnt"] == 2
    assert row["MES_prs"] == 10
    assert row["Creeler"] == "Alice"
    assert row["KO"] == "Bob"
    assert row["Tech"] == "Charlie"
    assert row["Yarner"] == "Dana"


def test_merge_staff_info_to_view_unmatched_staff_preserves_row_with_null_roles(
    monkeypatch,
):
    """
    A row without a matching staff schedule should remain with null role
    values.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_unmatched_staff_schedule_df(),
    )

    result = staff_info.merge_staff_info_to_view(
        _make_base_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
    )

    assert len(result) == 1
    row = result.iloc[0]

    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert row["Mach_cnt"] == 2
    assert row["MES_prs"] == 10
    for role_column in STAFF_ROLE_COLUMNS:
        assert row[role_column] is None


def test_merge_staff_info_to_view_empty_staff_schedule_preserves_row_with_null_roles(
    monkeypatch,
):
    """
    Empty staff schedule should not remove existing view rows.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_empty_staff_schedule_df(),
    )

    result = staff_info.merge_staff_info_to_view(
        _make_base_view_df(),
        start_time="2026-05-01",
        end_time="2026-05-02",
    )

    assert len(result) == 1
    row = result.iloc[0]

    assert row["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert row["Mach_cnt"] == 2
    assert row["MES_prs"] == 10
    for role_column in STAFF_ROLE_COLUMNS:
        assert row[role_column] is None


def test_merge_staff_info_to_view_converts_shift_start_time_to_timestamp_before_merge(
    monkeypatch,
):
    """
    String and Timestamp Shift_Start_Time values should both join to datetime
    staff rows and return formatted strings.
    """
    view_df = pd.DataFrame(
        {
            "id": [
                0,
                1,
            ],
            "Shift_Start_Time": [
                "2026-05-01 07:00:00",
                pd.Timestamp("2026-05-01 19:00:00"),
            ],
            "Mach_cnt": [
                2,
                3,
            ],
        }
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    result = staff_info.merge_staff_info_to_view(
        view_df,
        start_time="2026-05-01",
        end_time="2026-05-02",
    )

    result_by_shift = result.set_index("Shift_Start_Time")

    assert list(result["Shift_Start_Time"]) == [
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
    ]
    assert result["Shift_Start_Time"].map(type).eq(str).all()
    assert result_by_shift.loc["2026-05-01 07:00:00", "Creeler"] == "Alice"
    assert result_by_shift.loc["2026-05-01 19:00:00", "Creeler"] == "Evan"


def test_merge_staff_info_to_view_staff_lookup_arguments(monkeypatch):
    """
    get_staff_schedule_table should receive start_time and end_time unchanged.
    """
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    result = staff_info.merge_staff_info_to_view(
        _make_base_view_df(),
        start_time="2026-05-01 00:00:00",
        end_time="2026-05-02 00:00:00",
    )

    assert not result.empty
    staff_schedule_mock.assert_called_once_with(
        "2026-05-01 00:00:00",
        "2026-05-02 00:00:00",
    )
