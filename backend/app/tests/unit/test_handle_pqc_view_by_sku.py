"""
Test cases for handle_pqc_view_by_sku:

1. Extractor arguments
   - Verify _extract_pqc_data receives start, end, and shift.

2. Output schema
   - Verify the returned DataFrame has the expected columns.

3. Single SKU aggregation
   - Verify repeated rows for the same shift and style are grouped.

4. Full Style_Code grouping
   - Verify styles are grouped by full Style_Code, not the first token.

5. Multiple shifts
   - Verify the same style on different shifts returns separate rows.

6. Defect totals
   - Verify defects are summed from raw defect columns and are not halved.

7. Shift formatting and sorting
   - Verify Shift_Start_Time is sorted and formatted as a string.

8. Null Style_Code handling
   - Verify null Style_Code rows are dropped by groupby.

9. Empty extractor result
   - Verify an empty extracted DataFrame returns an empty result schema.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_pqc_data
from app.tests.mocks.extract_pqc_data_output_mocks import (
    make_base_pqc_sku_mach_detail_df,
    make_metrics_pqc_sku_mach_detail_df,
)


DEFECT_COLUMNS = [
    "toeHole",
    "brokenNDL",
    "missNDL",
    "fanYarn",
    "missYarn",
    "logoIssue",
    "dirty",
    "feisha",
    "other",
]

EXPECTED_COLUMNS = [
    "id",
    "Shift_Start_Time",
    "Style_Code",
    "pqc_cnt",
    *DEFECT_COLUMNS,
    "defects",
]


def _result_by_style(result: pd.DataFrame) -> dict:
    return {
        row["Style_Code"]: row
        for row in result.to_dict(orient="records")
    }


def _result_by_style_shift(result: pd.DataFrame) -> dict:
    return {
        (row["Style_Code"], row["Shift_Start_Time"]): row
        for row in result.to_dict(orient="records")
    }


def _make_same_style_multiple_shift_df() -> pd.DataFrame:
    df = make_base_pqc_sku_mach_detail_df()
    extra_shift_row = df[df["Style_Code"] == "ABC RED"].iloc[[0]].copy()
    extra_shift_row["Shift_Start_Time"] = pd.Timestamp("2026-05-01 19:00:00")
    return pd.concat([extra_shift_row, df], ignore_index=True)


def test_handle_pqc_view_by_sku_extract_pqc_data_arguments(monkeypatch):
    """
    handle_pqc_view_by_sku should pass the requested date range and shift to
    _extract_pqc_data.
    """
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_handle_pqc_view_by_sku_output_columns(monkeypatch):
    """
    Test final output schema.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS


def test_handle_pqc_view_by_sku_single_group_aggregation(monkeypatch):
    """
    Rows with the same Shift_Start_Time and Style_Code should be aggregated
    into one output row.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    abc_red = _result_by_style(result)["ABC RED"]

    assert abc_red["pqc_cnt"] == 2
    assert abc_red["toeHole"] == 2
    assert abc_red["brokenNDL"] == 1
    assert abc_red["missNDL"] == 1
    assert abc_red["defects"] == 4


def test_handle_pqc_view_by_sku_groups_by_full_style_code(monkeypatch):
    """
    The PQC SKU endpoint groups by full Style_Code. It should not collapse
    ABC RED and ABC BLUE into a single ABC row.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_base_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert set(result["Style_Code"]) == {
        "ABC BLUE",
        "ABC RED",
        "XYZ BLACK",
    }
    assert "ABC" not in set(result["Style_Code"])


def test_handle_pqc_view_by_sku_same_style_multiple_shifts(monkeypatch):
    """
    The same Style_Code on different shifts should produce separate output
    rows.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        _make_same_style_multiple_shift_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    result_by_style_shift = _result_by_style_shift(result)


    assert set(result_by_style_shift) == {
        ("ABC BLUE", "2026-05-01 07:00:00"),
        ("ABC RED", "2026-05-01 07:00:00"),
        ("ABC RED", "2026-05-01 19:00:00"),
        ("XYZ BLACK", "2026-05-01 07:00:00"),
    }
    assert result_by_style_shift[("ABC RED", "2026-05-01 07:00:00")]["pqc_cnt"] == 2
    assert result_by_style_shift[("ABC RED", "2026-05-01 19:00:00")]["pqc_cnt"] == 1


def test_handle_pqc_view_by_sku_defects_are_not_halved(monkeypatch):
    """
    handle_pqc_view_by_sku reports raw PQC defect totals. It should not apply
    the integer division used by PQC merge helpers.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        make_metrics_pqc_sku_mach_detail_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    abc_green = _result_by_style(result)["ABC GREEN"]

    assert abc_green["toeHole"] == 1
    assert abc_green["brokenNDL"] == 1
    assert abc_green["missNDL"] == 1
    assert abc_green["fanYarn"] == 1
    assert abc_green["missYarn"] == 1
    assert abc_green["logoIssue"] == 1
    assert abc_green["defects"] == 6


def test_handle_pqc_view_by_sku_sorts_and_formats_shift_start_time(monkeypatch):
    """
    Shift_Start_Time should be returned as an ascending formatted string.
    """
    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        _make_same_style_multiple_shift_df(),
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=0,
    )

    shift_values = result["Shift_Start_Time"].tolist()

    assert shift_values == sorted(shift_values)
    assert all(isinstance(value, str) for value in shift_values)
    assert set(shift_values) == {
        "2026-05-01 07:00:00",
        "2026-05-01 19:00:00",
    }


def test_handle_pqc_view_by_sku_null_style_code_is_dropped(monkeypatch):
    """
    pandas groupby drops null keys, so rows without Style_Code should not
    appear in the output.
    """
    df = make_base_pqc_sku_mach_detail_df()
    df.loc[df["Style_Code"] == "ABC BLUE", "Style_Code"] = None

    patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        df,
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert set(result["Style_Code"]) == {"ABC RED", "XYZ BLACK"}
    assert None not in result["Style_Code"].tolist()


def test_handle_pqc_view_by_sku_empty_df(monkeypatch):
    """
    Empty _extract_pqc_data output should return an empty DataFrame with the
    same output schema.
    """
    empty_df = make_base_pqc_sku_mach_detail_df().iloc[0:0].copy()
    extract_mock = patch_extract_pqc_data(
        monkeypatch,
        pqc_view,
        empty_df,
    )

    result = pqc_view.handle_pqc_view_by_sku(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS
    extract_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
        1,
    )
