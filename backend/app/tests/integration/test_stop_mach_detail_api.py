"""
Test cases for /base/stop/mach/detail API:

1. Output schema
   - Verify the API returns content records with expected stop detail and
     staff schedule fields.

2. Extractor arguments
   - Verify extract_base_data receives StopExtractor, start, and end, and
     staff schedule lookup receives start and end.

3. Empty extractor result
   - Verify an empty extracted DataFrame returns empty API content without
     querying staff schedule.

4. Representative transformation and serialization
   - Verify filtered detail rows serialize strings, ints, and timedeltas.

5. Required query validation
   - Verify missing required route parameters are rejected by FastAPI.
"""
from fastapi.testclient import TestClient

import app.services.staff_info as staff_info
import app.services.stop_view as stop_view
from app.main import app
from app.tests.mocks.common_mocks import (
    patch_extract_base_data,
    patch_get_staff_schedule_table,
)
from app.tests.mocks.handle_stop_mach_detail_mocks import (
    make_base_stop_mach_detail_df,
    make_empty_stop_mach_detail_df,
)
from app.tests.mocks.staff_schedule_mocks import make_base_staff_schedule_df
from extractors import StopExtractor


client = TestClient(app)


EXPECTED_COLUMNS = [
    "id",
    "Stop_code",
    "Description",
    "MachID",
    "Style_Code",
    "Stop_time",
    "Recover_time",
    "duration",
    "Shift_Start_Time",
    "Creeler",
    "KO",
    "Tech",
    "Yarner",
]


def _get_stop_mach_detail(**overrides):
    params = {
        "start": "2026-05-01",
        "end": "2026-05-02",
        "shift": 0,
        "mach": 1,
        "style": "ABC",
    }
    params.update(overrides)

    return client.get(
        "/base/stop/mach/detail",
        params=params,
    )


def test_stop_mach_detail_api_output_columns(monkeypatch):
    """
    Case 1: Output schema.
    Verify the API returns the expected top-level response and row fields.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = _get_stop_mach_detail()

    assert response.status_code == 200
    body = response.json()

    assert list(body.keys()) == ["content"]
    assert list(body["content"][0].keys()) == EXPECTED_COLUMNS


def test_stop_mach_detail_api_extract_base_data_arguments(monkeypatch):
    """
    Case 2: Extractor arguments.
    Verify the API path passes start and end to extract_base_data through
    handle_stop_mach_detail. Current behavior does not pass shift, mach, or
    style.
    """
    extract_mock = patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = _get_stop_mach_detail(shift=1, mach=1, style="ABC")

    assert response.status_code == 200
    extract_mock.assert_called_once_with(
        StopExtractor,
        "2026-05-01",
        "2026-05-02",
    )
    staff_schedule_mock.assert_called_once_with(
        "2026-05-01",
        "2026-05-02",
    )


def test_stop_mach_detail_api_empty_df(monkeypatch):
    """
    Case 3: Empty extractor result.
    If extract_base_data returns an empty DataFrame, the API should return
    empty content.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_empty_stop_mach_detail_df(),
    )
    staff_schedule_mock = patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = _get_stop_mach_detail()

    assert response.status_code == 200
    assert response.json() == {"content": []}
    staff_schedule_mock.assert_not_called()


def test_stop_mach_detail_api_detail_serialization(monkeypatch):
    """
    Case 4: Representative transformation and serialization.
    Verify filtered detail rows serialize strings, ints, and timedeltas.
    """
    patch_extract_base_data(
        monkeypatch,
        stop_view,
        make_base_stop_mach_detail_df(),
    )
    patch_get_staff_schedule_table(
        monkeypatch,
        staff_info,
        make_base_staff_schedule_df(),
    )

    response = _get_stop_mach_detail(mach=1, style="ABC")

    assert response.status_code == 200
    content = response.json()["content"]
    result_by_stop_code = {
        record["Stop_code"]: record
        for record in content
    }

    assert len(content) == 2
    assert set(result_by_stop_code) == {10, 20}

    stop_10 = result_by_stop_code[10]
    stop_20 = result_by_stop_code[20]

    assert stop_10["Description"] == "Jam"
    assert stop_10["MachID"] == 1
    assert stop_10["Style_Code"] == "ABC"
    assert stop_10["Stop_time"] == "2026-05-01 08:00:00"
    assert stop_10["Recover_time"] == "2026-05-01 08:05:00"
    assert stop_10["Shift_Start_Time"] == "2026-05-01 07:00:00"
    assert stop_10["duration"] == 300.0
    assert stop_10["Creeler"] == "Alice"
    assert stop_10["KO"] == "Bob"
    assert stop_10["Tech"] == "Charlie"
    assert stop_10["Yarner"] == "Dana"

    assert stop_20["Description"] == "Low Air"
    assert stop_20["duration"] == 900.0
    assert stop_20["Creeler"] == "Alice"


def test_stop_mach_detail_api_requires_query_params():
    """
    Case 5: Required query validation.
    Missing required route parameters should be rejected by FastAPI before
    the handler runs.
    """
    required_params = ["start", "end", "shift", "mach", "style"]

    for missing_param in required_params:
        params = {
            "start": "2026-05-01",
            "end": "2026-05-02",
            "shift": 0,
            "mach": 1,
            "style": "ABC",
        }
        params.pop(missing_param)

        response = client.get(
            "/base/stop/mach/detail",
            params=params,
        )

        assert response.status_code == 422
