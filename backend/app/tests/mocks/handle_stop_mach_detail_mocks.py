from datetime import timedelta

import pandas as pd


def make_empty_stop_mach_detail_df() -> pd.DataFrame:
    return pd.DataFrame()


def _make_row(
    mach_id: int,
    style_code,
    description,
    stop_time: str,
    minutes: int = 10,
    stop_code=None,
) -> dict:
    stop_ts = pd.Timestamp(stop_time)

    return {
        "Stop_code": stop_code if stop_code is not None else 10,
        "Description": description,
        "MachID": mach_id,
        "Style_Code": style_code,
        "Stop_time": stop_ts,
        "Recover_time": stop_ts + timedelta(minutes=minutes),
    }


def make_base_stop_mach_detail_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", " Jam ", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "Low Air", "2026-05-01 09:00:00", minutes=15, stop_code=20),
            _make_row(2, "ABC RED", "Other Mach", "2026-05-01 10:00:00", minutes=25, stop_code=30),
            _make_row(1, "XYZ RED", "Other Style", "2026-05-01 11:00:00", minutes=35, stop_code=40),
        ]
    )


def make_stop_mach_detail_style_normalization_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, " ABC RED ", "First ABC", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "Second ABC", "2026-05-01 08:10:00", minutes=10, stop_code=20),
            _make_row(1, "XYZ BLACK", "XYZ Style", "2026-05-01 08:20:00", minutes=20, stop_code=30),
            _make_row(2, " ABC GREEN ", "Other Mach ABC", "2026-05-01 08:30:00", minutes=30, stop_code=40),
        ]
    )


def make_stop_mach_detail_missing_style_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "Valid Style", "2026-05-01 08:00:00", minutes=8, stop_code=10),
            _make_row(1, "", "Blank Style", "2026-05-01 08:10:00", minutes=13, stop_code=20),
            _make_row(1, "   ", "Whitespace Style", "2026-05-01 08:20:00", minutes=21, stop_code=30),
            _make_row(1, None, "None Style", "2026-05-01 08:30:00", minutes=34, stop_code=40),
            _make_row(1, 123, "Non String Style", "2026-05-01 08:40:00", minutes=55, stop_code=50),
        ]
    )


def make_stop_mach_detail_shift_filter_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "Night Previous", "2026-05-01 05:30:00", minutes=6, stop_code=10),
            _make_row(1, "ABC BLUE", "Day Start", "2026-05-01 08:00:00", minutes=12, stop_code=20),
            _make_row(1, "ABC GREEN", "Day End", "2026-05-01 19:00:00", minutes=18, stop_code=30),
            _make_row(1, "ABC BLACK", "Night Start", "2026-05-01 19:01:00", minutes=24, stop_code=40),
            _make_row(1, "ABC WHITE", "Night End", "2026-05-01 07:00:00", minutes=30, stop_code=50),
            _make_row(2, "ABC RED", "Other Mach Day", "2026-05-01 08:15:00", minutes=36, stop_code=60),
            _make_row(1, "XYZ RED", "Other Style Day", "2026-05-01 08:30:00", minutes=42, stop_code=70),
        ]
    )


def make_stop_mach_detail_shift_boundary_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "Seven AM Included Night", "2026-05-01 07:00:00", minutes=7, stop_code=10),
            _make_row(1, "ABC BLUE", "Day After Seven", "2026-05-01 07:00:01", minutes=14, stop_code=20),
            _make_row(1, "ABC GREEN", "Seven PM Included Day", "2026-05-01 19:00:00", minutes=21, stop_code=30),
            _make_row(1, "ABC BLACK", "Night After Seven PM", "2026-05-01 19:00:01", minutes=28, stop_code=40),
        ]
    )


def make_stop_mach_detail_sorting_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "Day Short", "2026-05-01 08:00:00", minutes=5, stop_code=10),
            _make_row(1, "ABC BLUE", "Night Long", "2026-05-01 20:00:00", minutes=60, stop_code=20),
            _make_row(1, "ABC GREEN", "Day Long", "2026-05-01 09:00:00", minutes=30, stop_code=30),
            _make_row(1, "ABC BLACK", "Night Short", "2026-05-01 21:00:00", minutes=15, stop_code=40),
        ]
    )


def make_stop_mach_detail_null_conversion_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                **_make_row(
                    1,
                    "ABC RED",
                    None,
                    "2026-05-01 08:00:00",
                    minutes=10,
                    stop_code=10,
                ),
                "Optional_Note": None,
            },
            {
                **_make_row(
                    1,
                    "ABC BLUE",
                    "Has Note",
                    "2026-05-01 08:20:00",
                    minutes=20,
                    stop_code=20,
                ),
                "Optional_Note": "note",
            },
        ]
    )


def make_stop_mach_detail_filtered_empty_after_shift_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(1, "ABC RED", "Night Only One", "2026-05-01 06:30:00", minutes=11, stop_code=10),
            _make_row(1, "ABC BLUE", "Night Only Two", "2026-05-01 19:01:00", minutes=22, stop_code=20),
        ]
    )


def make_stop_mach_detail_no_matching_mach_style_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(2, "ABC RED", "Wrong Mach", "2026-05-01 08:00:00", minutes=10, stop_code=10),
            _make_row(1, "XYZ RED", "Wrong Style", "2026-05-01 08:10:00", minutes=20, stop_code=20),
        ]
    )
