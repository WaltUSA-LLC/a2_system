import pandas as pd


STAFF_ROLE_COLUMNS = [
    "Creeler",
    "KO",
    "Tech",
    "Yarner",
]


def make_empty_staff_schedule_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ShiftStartTime": pd.Series(dtype="datetime64[ns]"),
            "Creeler": pd.Series(dtype="object"),
            "KO": pd.Series(dtype="object"),
            "Tech": pd.Series(dtype="object"),
            "Yarner": pd.Series(dtype="object"),
        }
    )


def make_base_staff_schedule_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ShiftStartTime": [
                pd.Timestamp("2026-05-01 07:00:00"),
            ],
            "Creeler": [
                "Alice",
            ],
            "KO": [
                "Bob",
            ],
            "Tech": [
                "Charlie",
            ],
            "Yarner": [
                "Dana",
            ],
        }
    )


def make_multi_staff_schedule_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ShiftStartTime": [
                pd.Timestamp("2026-05-01 07:00:00"),
                pd.Timestamp("2026-05-01 19:00:00"),
            ],
            "Creeler": [
                "Alice",
                "Evan",
            ],
            "KO": [
                "Bob",
                "Fatima",
            ],
            "Tech": [
                "Charlie",
                "Grace",
            ],
            "Yarner": [
                "Dana",
                "Hugo",
            ],
        }
    )


def make_unmatched_staff_schedule_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ShiftStartTime": [
                pd.Timestamp("2026-05-02 07:00:00"),
            ],
            "Creeler": [
                "Iris",
            ],
            "KO": [
                "Jules",
            ],
            "Tech": [
                "Kai",
            ],
            "Yarner": [
                "Lena",
            ],
        }
    )
