"""
Test cases for _extract_pqc_data:

1. Extractor arguments
   - Verify extract_base_data receives PQCExtractor, start, end, and shift.

2. Shift_Start_Time construction
   - Verify Date and Shift are combined into a Timestamp column.

3. Role_Name parsing
   - Verify Role and Name are split and stripped from Role_Name.

4. Style_Code normalization
   - Verify non-empty strings are stripped and upper-cased, while invalid
     values become None.

5. Raw column preservation
   - Verify DateRec, MachID, Role_Name, and defect columns are preserved.

6. Empty extractor result
   - Verify an empty raw PQC DataFrame returns an empty normalized DataFrame.
"""

import pandas as pd

import app.services.pqc_view as pqc_view

from app.tests.mocks.common_mocks import patch_extract_base_data
from app.tests.mocks.extract_pqc_data_input_mocks import (
    make_base_raw_pqc_df,
    make_empty_raw_pqc_df,
    make_raw_pqc_df_with_invalid_style_code,
)


EXPECTED_COLUMNS = [
    "DateRec",
    "MachID",
    "Style_Code",
    "toeHole",
    "brokenNDL",
    "missNDL",
    "fanYarn",
    "missYarn",
    "logoIssue",
    "dirty",
    "feisha",
    "other",
    "Shift_Start_Time",
    "Role",
    "Name",
]


def test_extract_pqc_data_extract_base_data_arguments(monkeypatch):
    """
    _extract_pqc_data should call extract_base_data with PQCExtractor and
    the requested time range plus shift.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert not result.empty
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )


def test_extract_pqc_data_output_columns(monkeypatch):
    """
    Date and Shift should be replaced by the normalized Shift_Start_Time
    column, while derived Role and Name columns are added.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert list(result.columns) == EXPECTED_COLUMNS
    assert "Date" not in result.columns
    assert "Shift" not in result.columns
    assert "Role_Name" not in result.columns


def test_extract_pqc_data_builds_shift_start_time(monkeypatch):
    """
    Date and Shift should be combined into pandas Timestamps.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result["Shift_Start_Time"].tolist() == [
        pd.Timestamp("2026-05-01 07:00:00"),
        pd.Timestamp("2026-05-01 07:00:00"),
        pd.Timestamp("2026-05-01 07:00:00"),
    ]


def test_extract_pqc_data_splits_role_name(monkeypatch):
    """
    Role_Name should split into stripped Role and Name values.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result["Role"].tolist() == ["KO", "Tech", "KO"]
    assert result["Name"].tolist() == ["Alice", "Bob", "Alice"]


def test_extract_pqc_data_normalizes_style_code(monkeypatch):
    """
    Non-empty Style_Code strings should be stripped and upper-cased.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_base_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result["Style_Code"].tolist() == ["ABC RED", "ABC BLUE", "ABC RED"]


def test_extract_pqc_data_invalid_style_code_becomes_none(monkeypatch):
    """
    Empty, whitespace-only, and None Style_Code values should normalize to
    None.
    """
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_raw_pqc_df_with_invalid_style_code(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result["Style_Code"].tolist() == [None, None, None]


def test_extract_pqc_data_preserves_raw_columns(monkeypatch):
    """
    Raw non-normalized fields needed by downstream PQC views should remain
    unchanged.
    """
    raw_df = make_base_raw_pqc_df()
    patch_extract_base_data(
        monkeypatch,
        pqc_view,
        raw_df,
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result["MachID"].tolist() == raw_df["MachID"].tolist()
    assert result["DateRec"].tolist() == raw_df["DateRec"].tolist()
    assert result["toeHole"].tolist() == [1, 0, 1]
    assert result["brokenNDL"].tolist() == [0, 1, 0]
    assert result["missNDL"].tolist() == [0, 0, 1]
    assert result["missYarn"].tolist() == [0, 1, 0]


def test_extract_pqc_data_empty_df(monkeypatch):
    """
    An empty raw DataFrame with the expected raw columns should return an
    empty normalized DataFrame with the expected output columns.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        pqc_view,
        make_empty_raw_pqc_df(),
    )

    result = pqc_view._extract_pqc_data(
        start_time="2026-05-01",
        end_time="2026-05-02",
        shift=1,
    )

    assert result.empty
    assert list(result.columns) == EXPECTED_COLUMNS
    extract_mock.assert_called_once_with(
        pqc_view.PQCExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )