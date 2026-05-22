"""
Test cases for fetch_staff_info_by_date_and_shift:

1. Day shift filtering
   - Verify shift 1 returns only staff scheduled at 07:00.

2. Night shift filtering
   - Verify shift 2 returns only staff scheduled at 19:00.

3. Staff schedule lookup arguments
   - Verify the lookup receives the same date as start and end date.

4. No matching shift
   - Verify a valid shift with no matching ShiftStartTime returns empty staff
     rows without ShiftStartTime.

5. Empty staff schedule
   - Verify an empty schedule returns an empty DataFrame.

6. Null handling
   - Verify NaN role values are converted to None.

7. Invalid shift
   - Verify unsupported shift values raise ValueError.

8. Extra columns
   - Verify non-ShiftStartTime columns are preserved.
"""

import numpy as np
import pandas as pd
import pytest

import app.services.staff_info as staff_info

from app.tests.mocks.common_mocks import patch_get_staff_schedule_table
from app.tests.mocks.staff_schedule_mocks import (
    STAFF_ROLE_COLUMNS,
    make_empty_staff_schedule_df,
    make_multi_staff_schedule_df,
    make_unmatched_staff_schedule_df,
)


def test_fetch_staff_info_by_date_and_shift_day_shift(monkeypatch):
    """
    Shift 1 should return only the 07:00 staff schedule row.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=1,
    )

    assert len(result) == 1
    assert list(result.columns) == STAFF_ROLE_COLUMNS

    row = result.iloc[0]
    assert row["Creeler"] == "Alice"
    assert row["KO"] == "Bob"
    assert row["Tech"] == "Charlie"
    assert row["Yarner"] == "Dana"


def test_fetch_staff_info_by_date_and_shift_night_shift(monkeypatch):
    """
    Shift 2 should return only the 19:00 staff schedule row.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=2,
    )

    assert len(result) == 1
    assert list(result.columns) == STAFF_ROLE_COLUMNS

    row = result.iloc[0]
    assert row["Creeler"] == "Evan"
    assert row["KO"] == "Fatima"
    assert row["Tech"] == "Grace"
    assert row["Yarner"] == "Hugo"


def test_fetch_staff_info_by_date_and_shift_lookup_arguments(monkeypatch):
    """
    Staff schedule lookup should receive date as both start and end.
    """
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=1,
    )

    assert not result.empty
    staff_schedule_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
    )


def test_fetch_staff_info_by_date_and_shift_no_matching_shift(
    monkeypatch,
):
    """
    A valid shift with no matching ShiftStartTime should return empty staff
    rows and should not expose ShiftStartTime.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_unmatched_staff_schedule_df(),
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=2,
    )

    assert result.empty
    assert list(result.columns) == STAFF_ROLE_COLUMNS
    assert "ShiftStartTime" not in result.columns


def test_fetch_staff_info_by_date_and_shift_empty_schedule(monkeypatch):
    """
    Empty staff schedule should return an empty DataFrame for a valid shift.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_empty_staff_schedule_df(),
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=1,
    )

    assert result.empty
    assert list(result.columns) == STAFF_ROLE_COLUMNS


def test_fetch_staff_info_by_date_and_shift_nan_values_become_none(
    monkeypatch,
):
    """
    NaN staff role values should be converted to None before returning.
    """
    staff_schedule_df = pd.DataFrame(
        {
            "ShiftStartTime": [
                pd.Timestamp("2026-05-01 07:00:00"),
            ],
            "Creeler": [
                "Alice",
            ],
            "KO": [
                np.nan,
            ],
            "Tech": [
                "Charlie",
            ],
            "Yarner": [
                "Dana",
            ],
        }
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        staff_schedule_df,
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=1,
    )

    row = result.iloc[0]
    assert row["KO"] is None


def test_fetch_staff_info_by_date_and_shift_invalid_shift_raises(
    monkeypatch,
):
    """
    Unsupported shift values should raise ValueError.
    """
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    with pytest.raises(ValueError, match="Shift 3 is invalid"):
        staff_info.fetch_staff_info_by_date_and_shift(
            date="2026-05-01",
            shift=3,
        )


def test_fetch_staff_info_by_date_and_shift_preserves_extra_columns(
    monkeypatch,
):
    """
    Columns other than ShiftStartTime should be preserved.
    """
    staff_schedule_df = make_multi_staff_schedule_df()
    staff_schedule_df["Supervisor"] = [
        "Morgan",
        "Noor",
    ]
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        staff_schedule_df,
    )

    result = staff_info.fetch_staff_info_by_date_and_shift(
        date="2026-05-01",
        shift=1,
    )

    assert "ShiftStartTime" not in result.columns
    assert "Supervisor" in result.columns
    assert result.iloc[0]["Supervisor"] == "Morgan"
