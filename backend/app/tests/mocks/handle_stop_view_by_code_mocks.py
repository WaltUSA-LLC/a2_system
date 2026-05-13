from datetime import timedelta

import pandas as pd


def make_empty_stop_view_by_code_df() -> pd.DataFrame:
    return pd.DataFrame()


def _make_row(
    stop_code: int,
    description: str,
    mach_id: str,
    stop_time: str,
    minutes: int,
) -> dict:
    stop_ts = pd.Timestamp(stop_time)

    return {
        "Stop_code": stop_code,
        "Description": description,
        "MachID": mach_id,
        "Stop_time": stop_ts,
        "Recover_time": stop_ts + timedelta(minutes=minutes),
    }


def make_base_stop_view_by_code_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, " Jam ", "M1", "2026-05-01 08:00:00", 10),
            _make_row(10, "Jam", "M2", "2026-05-01 09:00:00", 20),
            _make_row(20, "Low Air", "M1", "2026-05-01 10:00:00", 5),
        ]
    )


def make_stop_view_by_code_df_with_duplicate_mach() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Jam", "M1", "2026-05-01 08:00:00", 10),
            _make_row(10, "Jam", "M1", "2026-05-01 09:00:00", 20),
            _make_row(10, "Jam", "M2", "2026-05-01 10:00:00", 30),
        ]
    )


def make_stop_view_by_code_shift_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Night Previous", "M1", "2026-05-01 5:30:00", 10),
            _make_row(20, "Day Start", "M2", "2026-05-01 08:00:00", 20),
            _make_row(30, "Day End", "M3", "2026-05-01 19:00:00", 30),
            _make_row(40, "Night Start", "M4", "2026-05-01 19:01:00", 40),
            _make_row(50, "Night End", "M4", "2026-05-01 07:00:00", 40),
        ]
    )


def make_stop_view_by_code_shift_boundary_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Seven AM Included Night", "M1", "2026-05-01 07:00:00", 10),
            _make_row(20, "Day After Seven", "M2", "2026-05-01 07:00:01", 20),
            _make_row(30, "Seven PM Included Day", "M3", "2026-05-01 19:00:00", 30),
            _make_row(40, "Night After Seven PM", "M4", "2026-05-01 19:00:01", 40),
        ]
    )


def make_stop_view_by_code_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Freq Tie Lower Mach", "M1", "2026-05-01 08:00:00", 5),
            _make_row(10, "Freq Tie Lower Mach", "M1", "2026-05-01 08:10:00", 10),
            _make_row(10, "Freq Tie Lower Mach", "M2", "2026-05-01 08:20:00", 15),
            _make_row(20, "Freq Tie Higher Mach", "M1", "2026-05-01 09:00:00", 5),
            _make_row(20, "Freq Tie Higher Mach", "M2", "2026-05-01 09:10:00", 10),
            _make_row(20, "Freq Tie Higher Mach", "M3", "2026-05-01 09:20:00", 12),
            _make_row(30, "Lower Frequency", "M1", "2026-05-01 10:00:00", 100),
            _make_row(30, "Lower Frequency", "M2", "2026-05-01 10:10:00", 100),
        ]
    )


def make_stop_view_by_code_chart_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Most Frequent", "M1", "2026-05-01 08:00:00", 10),
            _make_row(10, "Most Frequent", "M2", "2026-05-01 08:10:00", 10),
            _make_row(10, "Most Frequent", "M1", "2026-05-01 08:20:00", 10),
            _make_row(20, "Middle Duration", "M3", "2026-05-01 09:00:00", 40),
            _make_row(20, "Middle Duration", "M4", "2026-05-01 09:50:00", 60),
            _make_row(30, "Longest Duration", "M5", "2026-05-01 11:00:00", 200),
        ]
    )


def make_stop_view_by_code_chart_cap_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(
                stop_code=100 + index,
                description=f"Stop {index:02d}",
                mach_id=f"M{index:02d}",
                stop_time=f"2026-05-01 {8 + index:02d}:00:00",
                minutes=index + 1,
            )
            for index in range(12)
        ]
    )


def make_stop_view_by_code_filtered_empty_after_shift_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(10, "Night Only One", "M1", "2026-05-01 06:30:00", 10),
            _make_row(20, "Night Only Two", "M2", "2026-05-01 19:01:00", 20),
        ]
    )
