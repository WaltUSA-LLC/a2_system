from datetime import timedelta

import pandas as pd


def make_empty_stop_code_detail_df() -> pd.DataFrame:
    return pd.DataFrame()


def _make_row(
    mach_id: int,
    style_code,
    stop_time: str,
    minutes: int = 10,
    stop_code: int = 10,
) -> dict:
    stop_ts = pd.Timestamp(stop_time)

    return {
        "Stop_code": stop_code,
        "MachID": mach_id,
        "Style_Code": style_code,
        "Stop_time": stop_ts,
        "Recover_time": stop_ts + timedelta(minutes=minutes),
    }


def make_base_stop_code_detail_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:10:00", minutes=15, stop_code=10),
            _make_row(2, "ABC RED", "2026-05-01 08:30:00", minutes=30, stop_code=10),
            _make_row(1, "XYZ RED", "2026-05-01 09:00:00", minutes=25, stop_code=20),
        ]
    )


def make_stop_code_detail_stop_code_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:10:00", minutes=15, stop_code=10),
            _make_row(1, "ABC GREEN", "2026-05-01 08:20:00", minutes=20, stop_code=20),
            _make_row(2, "ABC RED", "2026-05-01 08:30:00", minutes=30, stop_code=30),
        ]
    )


def make_stop_code_detail_multiple_groups_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:10:00", minutes=15, stop_code=10),
            _make_row(1, "XYZ RED", "2026-05-01 08:30:00", minutes=25, stop_code=10),
            _make_row(2, "ABC RED", "2026-05-01 09:00:00", minutes=35, stop_code=10),
            _make_row(2, "XYZ RED", "2026-05-01 09:40:00", minutes=45, stop_code=10),
        ]
    )


def make_stop_code_detail_style_normalization_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, " ABC RED ", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:10:00", minutes=15, stop_code=10),
            _make_row(1, "XYZ BLACK", "2026-05-01 08:20:00", minutes=25, stop_code=10),
            _make_row(2, " ABC GREEN ", "2026-05-01 08:30:00", minutes=35, stop_code=10),
        ]
    )


def make_stop_code_detail_missing_style_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=8, stop_code=10),
            _make_row(1, "", "2026-05-01 08:10:00", minutes=13, stop_code=10),
            _make_row(1, "   ", "2026-05-01 08:20:00", minutes=21, stop_code=10),
            _make_row(1, None, "2026-05-01 08:30:00", minutes=34, stop_code=10),
            _make_row(1, 123, "2026-05-01 08:40:00", minutes=55, stop_code=10),
        ]
    )


def make_stop_code_detail_shift_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 05:30:00", minutes=6, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:00:00", minutes=12, stop_code=10),
            _make_row(1, "ABC GREEN", "2026-05-01 19:00:00", minutes=18, stop_code=10),
            _make_row(1, "ABC BLACK", "2026-05-01 19:01:00", minutes=24, stop_code=10),
            _make_row(1, "ABC WHITE", "2026-05-01 07:00:00", minutes=30, stop_code=10),
            _make_row(1, "XYZ RED", "2026-05-01 08:30:00", minutes=42, stop_code=20),
        ]
    )


def make_stop_code_detail_shift_boundary_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 07:00:00", minutes=7, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 07:00:01", minutes=14, stop_code=10),
            _make_row(1, "ABC GREEN", "2026-05-01 19:00:00", minutes=21, stop_code=10),
            _make_row(1, "ABC BLACK", "2026-05-01 19:00:01", minutes=28, stop_code=10),
        ]
    )


def make_stop_code_detail_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(2, "ABC RED", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "XYZ RED", "2026-05-01 08:10:00", minutes=10, stop_code=10),
            _make_row(1, "ABC RED", "2026-05-01 08:20:00", minutes=15, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:40:00", minutes=20, stop_code=10),
            _make_row(2, "XYZ RED", "2026-05-01 09:10:00", minutes=25, stop_code=10),
            _make_row(2, "XYZ BLUE", "2026-05-01 09:40:00", minutes=30, stop_code=10),
        ]
    )


def make_stop_code_detail_filtered_empty_after_shift_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 06:30:00", minutes=11, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 19:01:00", minutes=22, stop_code=10),
            _make_row(2, "ABC RED", "2026-05-01 08:00:00", minutes=33, stop_code=20),
        ]
    )


def make_stop_code_detail_no_matching_stop_code_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=10, stop_code=20),
            _make_row(2, "XYZ RED", "2026-05-01 08:10:00", minutes=20, stop_code=30),
        ]
    )


def make_stop_code_detail_median_duration_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "2026-05-01 08:10:00", minutes=15, stop_code=10),
            _make_row(1, "ABC GREEN", "2026-05-01 08:30:00", minutes=35, stop_code=10),
            _make_row(2, "XYZ RED", "2026-05-01 09:00:00", minutes=10, stop_code=10),
            _make_row(2, "XYZ BLUE", "2026-05-01 09:20:00", minutes=30, stop_code=10),
        ]
    )
