import pytest
import app.services.shift_view as shift_view
from app.services.shift_view import handle_shift_view
from app.tests.mocks.shift_view import mock_single_shift_data, \
    mock_mutiple_shifts_data, \
    mock_shutdown_mach_data, \
    mock_dupl_mach_data, \
    mock_empty_box_data, \
    mock_prs_weight_zero_data, \
    mock_prs_weight_nan_data, \
    mock_avg_cycle_zero_data, \
    mock_avg_cycle_nan_data

def test_handle_shift_view_agg_single_shift(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_single_shift_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")

    assert len(records) == 1
    assert records[0]["id"] == 0
    assert records[0]["Shift_Start_Time"] == "2026-04-30 07:00:00"
    assert records[0]["Mach_cnt"] == 2
    assert records[0]["NAU_prs"] == 44
    assert records[0]["MES_prs"] == 32.0
    assert records[0]["ST_prs"] == 45
    assert records[0]["eff"] == pytest.approx(0.711)
    assert records[0]["Time_Occupation"] == pytest.approx(0.714)


def test_handle_shift_view_agg_multiple_shifts(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_mutiple_shifts_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")

    assert len(records) == 2
    assert records[0]["id"] == 0
    assert records[0]["Shift_Start_Time"] == "2026-04-30 07:00:00"
    assert records[0]["Mach_cnt"] == 2
    assert records[0]["NAU_prs"] == 44
    assert records[0]["MES_prs"] == 32.0
    assert records[0]["ST_prs"] == 45
    assert records[0]["eff"] == pytest.approx(0.711)
    assert records[0]["Time_Occupation"] == pytest.approx(0.714)
    assert records[1]["id"] == 1
    assert records[1]["Shift_Start_Time"] == "2026-04-30 19:00:00"
    assert records[1]["Mach_cnt"] == 1
    assert records[1]["NAU_prs"] == 99
    assert records[1]["MES_prs"] == 10.0
    assert records[1]["ST_prs"] == 8
    assert records[1]["eff"] == pytest.approx(1.250)
    assert records[1]["Time_Occupation"] == pytest.approx(0.800)



def test_handle_shift_view_with_shudown_mach(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_shutdown_mach_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")

    assert len(records) == 1
    assert records[0]["Shift_Start_Time"] != "2026-04-30 7:00:00"


def test_handle_shift_view_with_dupl_mach(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_dupl_mach_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")

    assert len(records) == 2
    assert records[0]["Shift_Start_Time"] == "2026-04-30 07:00:00"
    assert records[0]["Mach_cnt"] == 1
    assert records[1]["Shift_Start_Time"] == "2026-04-30 19:00:00"
    assert records[1]["Mach_cnt"] == 1


def test_handle_shift_view_zero_weight(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_empty_box_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")
    assert records[0]["MES_prs"] == 0


def test_handle_shift_view_zero_mes_prs(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_prs_weight_zero_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")
    assert records[0]["MES_prs"] == 100


def test_handle_shift_view_nan_mes_prs(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_prs_weight_nan_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")
    assert records[0]["MES_prs"] == 100


def test_handle_shift_view_zero_st_prs(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_avg_cycle_zero_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")
    assert records[0]["ST_prs"] == 15


def test_handle_shift_view_nan_st_prs(monkeypatch):
    monkeypatch.setattr(shift_view,
        "extract_base_data",
        mock_avg_cycle_nan_data
    )

    result = handle_shift_view("2026-04-30", "2026-04-30", 0)
    records = result.to_dict(orient="records")
    assert records[0]["ST_prs"] == 0

    
