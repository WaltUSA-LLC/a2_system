"""
Test cases for /base/shift/detail API:

1. Output schema
   - Verify the API returns machine-detail and staff records with expected
     fields.

2. Extractor arguments
   - Verify extract_base_data receives MESExtractor, start as both start/end,
     and shift.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content.

4. Metric and comment serialization
   - Verify calculated metrics and comments are returned as JSON-safe values.

5. Duplicate machine rows
   - Verify duplicate MachID rows are preserved as detail records.

6. Night shift staff
   - Verify shift 2 returns the 19:00 staff record.

7. No matching staff
   - Verify a valid shift with no matching staff row returns empty staff.

8. Empty staff schedule
   - Verify an empty staff schedule returns empty staff while preserving
     machine-detail content.
"""

import pytest
from fastapi.testclient import TestClient

import app.services.staff_info as staff_info
import app.services.shift_view as shift_view
from app.main import app
from app.tests.mocks.common_mocks import (
    patch_extract_base_data,
    patch_get_staff_schedule_table,
)
from app.tests.mocks.handle_shift_mach_detail_mocks import (
    make_base_shift_mach_detail_df,
    make_empty_shift_mach_detail_df,
    make_shift_mach_detail_df_for_metrics_and_comments,
    make_shift_mach_detail_df_with_duplicate_mach,
)
from app.tests.mocks.staff_schedule_mocks import (
    STAFF_ROLE_COLUMNS,
    make_base_staff_schedule_df,
    make_empty_staff_schedule_df,
    make_multi_staff_schedule_df,
)
from extractors import MESExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "MachID",
    "Shift_Start_Time",
    "Style_Code",
    "Weight",
    "MES_prs",
    "NAU_prs",
    "ON_Time",
    "OFF_Time",
    "ON_Time_Occupation",
    "Mach_Efficiency",
    "Comment",
]


def test_shift_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns machine-detail and staff records with expected
    fields.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    content = payload["content"]
    staff = payload["staff"]

    assert list(payload.keys()) == ["content", "staff"]
    assert len(content) == 3
    assert list(content[0].keys()) == EXPECTED_COLUMNS
    assert len(staff) == 1
    assert list(staff[0].keys()) == STAFF_ROLE_COLUMNS


def test_shift_detail_api_detail_and_staff_lookup_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify that the API path passes start as both start_time and end_time,
    plus shift, to extract_base_data through handle_shift_mach_detail.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )
    staff_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-01",
        1,
    )
    staff_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
    )


def test_shift_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_empty_shift_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["content"] == []
    assert payload["staff"] == [
        {
            "Creeler": "Alice",
            "KO": "Bob",
            "Tech": "Charlie",
            "Yarner": "Dana",
        }
    ]


def test_shift_detail_api_metrics_and_comments(monkeypatch):
    """
    Case 4: Metric and comment serialization.
    Metric calculations should be serialized through the API, and comments
    should reflect machine efficiency.
    """
    df = make_shift_mach_detail_df_for_metrics_and_comments()
    df.loc[df["MachID"] == "M_LOW", ["ON_Time", "OFF_Time", "Avg_Cycle", "Weight"]] = [
        90,
        10,
        10,
        1,
    ]

    patch_extract_base_data(
        monkeypatch,
        shift_view,
        df,
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    result_by_mach = {
        record["MachID"]: record
        for record in content
    }

    good = result_by_mach["M_GOOD"]
    low = result_by_mach["M_LOW"]

    assert good["MES_prs"] == 9
    assert good["ON_Time_Occupation"] == pytest.approx(0.9)
    assert good["Mach_Efficiency"] == pytest.approx(1.8)
    assert good["Comment"] == "Good"

    assert low["MES_prs"] == 1
    assert low["ON_Time_Occupation"] == pytest.approx(0.9)
    assert low["Mach_Efficiency"] == pytest.approx(0.2)
    assert low["Comment"] == "Low Ef"


def test_shift_detail_api_duplicate_mach_rows_preserved(monkeypatch):
    """
    Case 5: Duplicate machine rows.
    Duplicate MachID rows should remain separate detail records.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_shift_mach_detail_df_with_duplicate_mach(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    m1_records = [
        record
        for record in content
        if record["MachID"] == "M1"
    ]

    assert len(content) == 3
    assert len(m1_records) == 2


def test_shift_detail_api_night_shift_staff(monkeypatch):
    """
    Case 6: Night shift staff.
    Verify shift 2 returns the staff record scheduled at 19:00.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["staff"] == [
        {
            "Creeler": "Evan",
            "KO": "Fatima",
            "Tech": "Grace",
            "Yarner": "Hugo",
        }
    ]


def test_shift_detail_api_no_matching_staff_returns_empty_staff(
    monkeypatch,
):
    """
    Case 7: No matching staff.
    If the schedule lookup has no row for the requested shift start time, the
    API should return an empty staff list.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["staff"] == []


def test_shift_detail_api_empty_staff_schedule_returns_empty_staff(
    monkeypatch,
):
    """
    Case 8: Empty staff schedule.
    If staff schedule lookup returns an empty DataFrame, the API should return
    empty staff while preserving machine-detail content.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_empty_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift/detail",
        params={
            "start": "2026-05-01",
            "shift": 1,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert len(payload["content"]) == 3
    assert payload["staff"] == []
