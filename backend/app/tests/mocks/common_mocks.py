import math
from unittest.mock import Mock

import pandas as pd
import numpy as np

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
    
    mock_extract_base_data = Mock(side_effect=fake_extract_base_data)

    monkeypatch.setattr(
        module,
        "extract_base_data",
        mock_extract_base_data,
    )

    return mock_extract_base_data


def patch_get_staff_schedule_table(monkeypatch, module, df: pd.DataFrame):
    """
    Patch get_staff_schedule_table inside the module under test.

    Example:
        patch_get_staff_schedule_table(monkeypatch, shift_view, make_base_shift_df())
    """

    def fake_get_staff_schedule_table(start_time, end_time):
        return df.copy()
    
    mock_get_staff_schedule_table = Mock(side_effect=fake_get_staff_schedule_table)

    monkeypatch.setattr(
        module,
        "get_staff_schedule_table",
        mock_get_staff_schedule_table,
    )

    return mock_get_staff_schedule_table


def patch_merge_staff_info_to_view(monkeypatch, module):
    """
    Patch merge_staff_info_to_view inside the module under test.
    If df is omitted, the patched merge returns the input view DataFrame.

    Example:
        patch_merge_staff_info_to_view(
            monkeypatch,
            shift_view,
            make_base_shift_view_df(),
        )
    """

    def fake_merge_staff_info_to_view(view_df, start_time, end_time):
        df = view_df.copy()
        df = df.replace([np.nan, np.inf, -np.inf], None)
        return df
    
    mock_merge_staff_info_to_view = Mock(side_effect=fake_merge_staff_info_to_view)

    monkeypatch.setattr(
        module,
        "merge_staff_info_to_view",
        mock_merge_staff_info_to_view,
    )

    return mock_merge_staff_info_to_view


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
