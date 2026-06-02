"""
Test cases for /base/sku/detail API:

1. Output schema
   - Verify the API returns SKU machine-detail and staff records with
     expected fields.

2. Detail and staff lookup arguments
   - Verify extract_base_data receives MESExtractor, start, end, and shift,
     and staff lookup receives start as both start/end.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content.

4. Style filtering
   - Verify style filtering uses Style_Code without size/color suffix.

5. No matching style
   - Verify no matching style returns empty API content.

6. Metric and comment serialization
   - Verify Discard_prs, calculated metrics, and comments are returned as
     JSON-safe values.

7. Night shift staff
   - Verify shift 2 returns the 19:00 staff record.

8. No matching staff
   - Verify a valid shift with no matching staff row returns empty staff.

9. Empty staff schedule
   - Verify an empty staff schedule returns empty staff while preserving
     SKU machine-detail content.
"""

import pytest
from fastapi.testclient import TestClient

import app.services.staff_info as staff_info
import app.services.sku_view as sku_view
from app.main import app
from app.tests.mocks.common_mocks import (
    patch_extract_base_data,
    patch_get_staff_schedule_table,
)
from app.tests.mocks.handle_sku_mach_detail_mocks import (
    make_base_sku_mach_detail_df,
    make_empty_sku_mach_detail_df,
    make_sku_mach_detail_df_for_metrics_and_comments,
    make_sku_mach_detail_df_without_matching_style,
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
    "MES_prs",
    "NAU_prs",
    "Discard_prs",
    "ON_Time",
    "OFF_Time",
    "ON_Time_Occupation",
    "Mach_Efficiency",
    "Comment",
]


def test_sku_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns SKU machine-detail and staff records with expected
    fields.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    content = payload["content"]
    staff = payload["staff"]

    assert list(payload.keys()) == ["content", "staff"]
    assert len(content) == 2
    assert list(content[0].keys()) == EXPECTED_COLUMNS
    assert len(staff) == 1
    assert list(staff[0].keys()) == STAFF_ROLE_COLUMNS


def test_sku_detail_api_detail_and_staff_lookup_arguments(monkeypatch):
    """
    Case 2: Detail and staff lookup arguments.
    Verify that the API path passes request query parameters to
    extract_base_data through handle_sku_mach_detail, and passes start as both
    start and end date to the staff schedule lookup.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    staff_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )
    staff_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-01",
    )


def test_sku_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_empty_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
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


def test_sku_detail_api_filters_by_style_without_size(monkeypatch):
    """
    Case 4: Style filtering.
    Style filtering should use the first token of Style_Code after stripping
    and uppercasing, while final Style_Code keeps the full cleaned value.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2
    assert {row["Style_Code"] for row in content} == {"ABC RED", "ABC BLUE"}
    assert "XYZ BLACK" not in {row["Style_Code"] for row in content}


def test_sku_detail_api_no_matching_style_returns_empty(monkeypatch):
    """
    Case 5: No matching style.
    If no row matches style, the API should return empty content.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_sku_mach_detail_df_without_matching_style(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
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


def test_sku_detail_api_metrics_and_comments(monkeypatch):
    """
    Case 6: Metric and comment serialization.
    Metric calculations should be serialized through the API, and comments
    should reflect machine efficiency.
    """
    df = make_sku_mach_detail_df_for_metrics_and_comments()
    df.loc[df["MachID"] == "M2", "Weight"] = 1
    df.loc[df["MachID"] == "M3", ["ON_Time", "OFF_Time", "Avg_Cycle"]] = [
        4,
        2,
        1,
    ]

    patch_extract_base_data(
        monkeypatch,
        sku_view,
        df,
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    result_by_mach = {
        record["MachID"]: record
        for record in content
    }

    good = result_by_mach["M1"]
    low = result_by_mach["M2"]
    rounded_low = result_by_mach["M3"]

    assert good["MES_prs"] == 8
    assert good["Discard_prs"] == 1
    assert good["ON_Time_Occupation"] == pytest.approx(0.8)
    assert good["Mach_Efficiency"] == pytest.approx(1.6)
    assert good["Comment"] == "Good"

    assert low["MES_prs"] == 1
    assert low["Discard_prs"] == 2
    assert low["ON_Time_Occupation"] == pytest.approx(0.5)
    assert low["Mach_Efficiency"] == pytest.approx(0.2)
    assert low["Comment"] == "Low Ef"

    assert rounded_low["MES_prs"] == 1
    assert rounded_low["Discard_prs"] == 3
    assert rounded_low["ON_Time_Occupation"] == pytest.approx(0.667)
    assert rounded_low["Mach_Efficiency"] == pytest.approx(0.333)
    assert rounded_low["Comment"] == "Low Ef"


def test_sku_detail_api_night_shift_staff(monkeypatch):
    """
    Case 7: Night shift staff.
    Verify shift 2 returns the staff record scheduled at 19:00.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_multi_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 2,
            "style": "ABC",
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


def test_sku_detail_api_no_matching_staff_returns_empty_staff(
    monkeypatch,
):
    """
    Case 8: No matching staff.
    If the schedule lookup has no row for the requested shift start time, the
    API should return an empty staff list.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 2,
            "style": "ABC",
        },
    )

    assert response.status_code == 200
    assert response.json()["staff"] == []


def test_sku_detail_api_empty_staff_schedule_returns_empty_staff(
    monkeypatch,
):
    """
    Case 9: Empty staff schedule.
    If staff schedule lookup returns an empty DataFrame, the API should return
    empty staff while preserving SKU machine-detail content.
    """
    patch_extract_base_data(
        monkeypatch,
        sku_view,
        make_base_sku_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_empty_staff_schedule_df(),
    )

    response = client.get(
        "/base/sku/detail",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
            "style": "ABC",
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert len(payload["content"]) == 2
    assert payload["staff"] == []
