from datetime import timedelta

import pandas as pd


def make_empty_stop_view_by_mach_df() -> pd.DataFrame:
    return pd.DataFrame()


def _make_row(
    mach_id: str,
    style_code,
    description: str,
    stop_time: str,
    minutes: int = 10,
    stop_code: int = 10,
) -> dict:
    stop_ts = pd.Timestamp(stop_time)

    return {
        "Stop_code": stop_code,
        "Description": description,
        "MachID": mach_id,
        "Style_Code": style_code,
        "Stop_time": stop_ts,
        "Recover_time": stop_ts + timedelta(minutes=minutes),
    }


def make_base_stop_view_by_mach_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "ABC RED", " Jam ", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row("M1", "ABC BLUE", "Jam", "2026-05-01 09:00:00", minutes=15, stop_code=20),
            _make_row("M2", "XYZ", "Low Air", "2026-05-01 10:00:00", minutes=25, stop_code=10),
        ]
    )


def make_stop_view_by_mach_style_normalization_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", " ABC RED ", "Jam", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row("M1", "ABC BLUE", "Jam", "2026-05-01 08:10:00", minutes=10, stop_code=20),
            _make_row("M1", "XYZ BLACK", "Jam", "2026-05-01 08:20:00", minutes=20, stop_code=10),
            _make_row("M2", " XYZ ", "Low Air", "2026-05-01 08:30:00", minutes=30, stop_code=20),
        ]
    )


def make_stop_view_by_mach_missing_style_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "ABC RED", "Valid Style", "2026-05-01 08:00:00", minutes=8, stop_code=10),
            _make_row("M1", "", "Blank Style", "2026-05-01 08:10:00", minutes=13, stop_code=20),
            _make_row("M1", None, "None Style", "2026-05-01 08:20:00", minutes=21, stop_code=10),
            _make_row("M2", 123, "Non String Style", "2026-05-01 08:30:00", minutes=34, stop_code=20),
        ]
    )


def make_stop_view_by_mach_shift_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "NIGHT PREV", "Night Previous", "2026-05-01 05:30:00", minutes=6, stop_code=10),
            _make_row("M2", "DAY START", "Day Start", "2026-05-01 08:00:00", minutes=12, stop_code=20),
            _make_row("M3", "DAY END", "Day End", "2026-05-01 19:00:00", minutes=18, stop_code=10),
            _make_row("M4", "NIGHT START", "Night Start", "2026-05-01 19:01:00", minutes=24, stop_code=20),
            _make_row("M5", "NIGHT END", "Night End", "2026-05-01 07:00:00", minutes=30, stop_code=10),
        ]
    )


def make_stop_view_by_mach_shift_boundary_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "BOUNDARY", "Seven AM Included Night", "2026-05-01 07:00:00", minutes=7, stop_code=10),
            _make_row("M2", "BOUNDARY", "Day After Seven", "2026-05-01 07:00:01", minutes=14, stop_code=20),
            _make_row("M3", "BOUNDARY", "Seven PM Included Day", "2026-05-01 19:00:00", minutes=21, stop_code=10),
            _make_row("M4", "BOUNDARY", "Night After Seven PM", "2026-05-01 19:00:01", minutes=28, stop_code=20),
        ]
    )


def make_stop_view_by_mach_table_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M2", "BBB RED", "M2 BBB 1", "2026-05-01 08:00:00", minutes=4, stop_code=10),
            _make_row("M1", "ZZZ RED", "M1 ZZZ 1", "2026-05-01 08:10:00", minutes=9, stop_code=20),
            _make_row("M1", "AAA RED", "M1 AAA 1", "2026-05-01 08:20:00", minutes=14, stop_code=10),
            _make_row("M1", "AAA BLUE", "M1 AAA 2", "2026-05-01 08:30:00", minutes=19, stop_code=20),
            _make_row("M2", "AAA RED", "M2 AAA 1", "2026-05-01 08:40:00", minutes=24, stop_code=10),
            _make_row("M2", "AAA BLUE", "M2 AAA 2", "2026-05-01 08:50:00", minutes=29, stop_code=20),
        ]
    )


def make_stop_view_by_mach_chart_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "ABC RED", "Most 1", "2026-05-01 08:00:00", minutes=3, stop_code=10),
            _make_row("M1", "ABC BLUE", "Most 2", "2026-05-01 08:10:00", minutes=6, stop_code=20),
            _make_row("M1", "ABC GREEN", "Most 3", "2026-05-01 08:20:00", minutes=9, stop_code=30),
            _make_row("M2", "XYZ RED", "Middle 1", "2026-05-01 08:30:00", minutes=12, stop_code=10),
            _make_row("M2", "XYZ BLUE", "Middle 2", "2026-05-01 08:40:00", minutes=15, stop_code=20),
            _make_row("M3", "DEF RED", "Least 1", "2026-05-01 08:50:00", minutes=18, stop_code=10),
        ]
    )


def make_stop_view_by_mach_chart_cap_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(
                mach_id=f"M{index:02d}",
                style_code=f"STYLE{index:02d} RED",
                description=f"Stop {index:02d}",
                stop_time=f"2026-05-01 {8 + index:02d}:00:00",
                minutes=index + 1,
                stop_code=10 + (index % 2) * 10,
            )
            for index in range(11)
        ]
    )


def make_stop_view_by_mach_filtered_empty_after_shift_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row("M1", "NIGHT ONE", "Night Only One", "2026-05-01 06:30:00", minutes=11, stop_code=10),
            _make_row("M2", "NIGHT TWO", "Night Only Two", "2026-05-01 19:01:00", minutes=22, stop_code=20),
        ]
    )
