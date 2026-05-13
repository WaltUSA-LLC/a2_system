import math
from unittest.mock import Mock

import numpy as np
import pandas as pd


def fake_distribute_weight_for_same_mach(df: pd.DataFrame) -> pd.DataFrame:
    return df


def fake_clean_weight(df: pd.DataFrame) -> pd.DataFrame:
    return df


def fake_filter_shutdown_mach(df: pd.DataFrame) -> pd.DataFrame:
    return df


def fake_estimate_mes_output_prs(row: pd.Series) -> int:
    return math.floor(row["Weight"])


def fake_estimate_st_output_prs(row: pd.Series) -> int | float:
    return row["Avg_Cycle"]


def make_call_counting_mocks():
    return {
        "distributeWeightForSameMach": Mock(
            side_effect=fake_distribute_weight_for_same_mach
        ),
        "clean_weight": Mock(
            side_effect=fake_clean_weight
        ),
        "filterShutdownMach": Mock(
            side_effect=fake_filter_shutdown_mach
        ),
        "estimate_mes_output_prs": Mock(
            side_effect=fake_estimate_mes_output_prs
        ),
        "estimate_st_output_prs": Mock(
            side_effect=fake_estimate_st_output_prs
        ),
    }


def patch_extract_base_data(monkeypatch, module, df: pd.DataFrame):
    """
    Patch extract_base_data inside the module under test.

    Example:
        patch_extract_base_data(monkeypatch, sku_view, make_base_sku_df())
    """

    def fake_extract_base_data(extractor_cls, start_time, end_time, shift=0):
        return df.copy()

    monkeypatch.setattr(
        module,
        "extract_base_data",
        fake_extract_base_data,
    )


def patch_common_dependencies(monkeypatch, module, mocks: dict):
    """
    Patch common helper functions with Mock objects.

    Example:
        mocks = make_call_counting_mocks()
        patch_call_counting_dependencies(monkeypatch, sku_view, mocks)
    """

    monkeypatch.setattr(
        module,
        "distributeWeightForSameMach",
        mocks["distributeWeightForSameMach"],
    )
    monkeypatch.setattr(
        module,
        "clean_weight",
        mocks["clean_weight"],
    )
    monkeypatch.setattr(
        module,
        "filterShutdownMach",
        mocks["filterShutdownMach"],
    )
    monkeypatch.setattr(
        module,
        "estimate_mes_output_prs",
        mocks["estimate_mes_output_prs"],
    )
    monkeypatch.setattr(
        module,
        "estimate_st_output_prs",
        mocks["estimate_st_output_prs"],
    )