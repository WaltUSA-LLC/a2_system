"""
Test cases for /base/shift API:

1. Output schema
   - Verify the API returns content records with expected shift and staff
     schedule fields.

2. Extractor arguments
   - Verify extract_base_data receives MESExtractor, start, end, and shift,
     and staff schedule lookup receives start and end.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content without
     querying staff schedule.

4. Single-shift aggregation
   - Verify one Shift_Start_Time group is aggregated and serialized with
     matching staff schedule fields.

5. Multiple-shift aggregation
   - Verify multiple Shift_Start_Time groups produce multiple API records
     with their matching staff schedule fields.
"""

import pytest
from fastapi.testclient import TestClient

import app.services.shift_view as shift_view
from app.main import app
from app.tests.mocks.common_mocks import (
    patch_extract_base_data,
    patch_get_staff_schedule_table,
)
from app.tests.mocks.handle_shift_view_mocks import (
    make_base_shift_df,
    make_empty_shift_df,
    make_multi_shift_df,
)
from app.tests.mocks.staff_schedule_mocks import (
    make_base_staff_schedule_df,
    make_multi_staff_schedule_df,
)
from extractors import MESExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "Shift_Start_Time",
    "Mach_cnt",
    "NAU_prs",
    "MES_prs",
    "ST_prs",
    "eff",
    "Time_Occupation",
    "Creeler",
    "KO",
    "Tech",
    "Yarner",
]


def test_shift_api_output_columns(monkeypatch):
    """
    Test final API response schema.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        shift_view,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    assert list(content[0].keys()) == EXPECTED_COLUMNS


def test_shift_api_extract_base_data_arguments(monkeypatch):
    """
    Verify that the API path passes request query parameters to
    extract_base_data through handle_shift_view.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_df(),
    )
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        shift_view,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        MESExtractor,
        "2026-05-01",
        "2026-05-02",
        1,
    )
    staff_schedule_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
    )


def test_shift_api_empty_df(monkeypatch):
    """
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_empty_shift_df(),
    )
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        shift_view,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"content": []}
    staff_schedule_mock.assert_not_called()


def test_shift_api_single_shift_aggregation(monkeypatch):
    """
    Normal case:
    three machine rows are grouped into one shift group and serialized.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_base_shift_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        shift_view,
        make_base_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 1
    row = content[0]
    assert row["id"] == 0
    assert row["Shift_Start_Time"] == "2026-05-01 08:00:00"
    assert row["Mach_cnt"] == 2
    assert row["NAU_prs"] == 8
    assert row["MES_prs"] == 7
    assert row["ST_prs"] == 10
    assert row["eff"] == pytest.approx(0.7)
    assert row["Time_Occupation"] == pytest.approx(0.85)
    assert row["Creeler"] == "Alice"
    assert row["KO"] == "Bob"
    assert row["Tech"] == "Charlie"
    assert row["Yarner"] == "Dana"


def test_shift_api_multiple_shift_aggregation(monkeypatch):
    """
    Multiple shift groups should produce multiple API records.
    """
    patch_extract_base_data(
        monkeypatch,
        shift_view,
        make_multi_shift_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        shift_view,
        make_multi_staff_schedule_df(),
    )

    response = client.get(
        "/base/shift",
        params={
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 1,
        },
    )

    assert response.status_code == 200
    content = response.json()["content"]

    assert len(content) == 2

    result_by_shift = {
        record["Shift_Start_Time"]: record
        for record in content
    }

    shift_1 = result_by_shift["2026-05-01 08:00:00"]
    shift_2 = result_by_shift["2026-05-01 20:00:00"]

    assert shift_1["Mach_cnt"] == 2
    assert shift_1["NAU_prs"] == 6
    assert shift_1["MES_prs"] == 8
    assert shift_1["ST_prs"] == 9
    assert shift_1["eff"] == pytest.approx(0.889)
    assert shift_1["Time_Occupation"] == pytest.approx(0.889)
    assert shift_1["Creeler"] == "Alice"
    assert shift_1["KO"] == "Bob"
    assert shift_1["Tech"] == "Charlie"
    assert shift_1["Yarner"] == "Dana"

    assert shift_2["Mach_cnt"] == 2
    assert shift_2["NAU_prs"] == 10
    assert shift_2["MES_prs"] == 10
    assert shift_2["ST_prs"] == 6
    assert shift_2["eff"] == pytest.approx(1.667)
    assert shift_2["Time_Occupation"] == pytest.approx(0.75)
    assert shift_2["Creeler"] == "Evan"
    assert shift_2["KO"] == "Fatima"
    assert shift_2["Tech"] == "Grace"
    assert shift_2["Yarner"] == "Hugo"
