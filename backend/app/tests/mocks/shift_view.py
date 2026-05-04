import pandas as pd
import numpy as np

def mock_single_shift_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 12.0,
            "Prs_Weight": 1000,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 2,
            "Style_Code": "B",
            "Weight": 20.0,
            "Prs_Weight": 1000,
            "NAU_prs": 19,
            "ON_Time": 900,
            "OFF_Time": 300,
            "Avg_Cycle": 20,
        },  
    ])


def mock_mutiple_shifts_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 12.0,
            "Prs_Weight": 1000,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 2,
            "Style_Code": "B",
            "Weight": 20.0,
            "Prs_Weight": 1000,
            "NAU_prs": 19,
            "ON_Time": 900,
            "OFF_Time": 300,
            "Avg_Cycle": 20,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 19:00:00"),
            "MachID": 1,
            "Style_Code": "C",
            "Weight": 15,
            "Prs_Weight": 1500,
            "NAU_prs": 99,
            "ON_Time": 400,
            "OFF_Time": 100,
            "Avg_Cycle": 30,
        },
    ])


def mock_shutdown_mach_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 19:00:00"),
            "Style_Code": "A",
            "MachID": 1,
            "Weight": 12.0,
            "Prs_Weight": 1000,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 2,
            "Style_Code": "A",
            "Weight": 20.0,
            "Prs_Weight": 1000,
            "NAU_prs": 19,
            "ON_Time": 300,
            "OFF_Time": 300,
            "Avg_Cycle": 20,
        },
    ])


def mock_dupl_mach_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 12.0,
            "Prs_Weight": 1000,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "B",
            "Weight": 20.0,
            "Prs_Weight": 1000,
            "NAU_prs": 19,
            "ON_Time": 900,
            "OFF_Time": 300,
            "Avg_Cycle": 20,
        }, 
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 19:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 12.0,
            "Prs_Weight": 1000,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 19:00:00"),
            "MachID": 1,
            "Style_Code": "B",
            "Weight": 20.0,
            "Prs_Weight": 1000,
            "NAU_prs": 19,
            "ON_Time": 900,
            "OFF_Time": 300,
            "Avg_Cycle": 20,
        },  
    ])


def mock_empty_box_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 0.9,
            "Prs_Weight": 1,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
    ])


def mock_prs_weight_zero_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 10,
            "Prs_Weight": 0,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 1,
            "Prs_Weight": 10,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
    ])


def mock_prs_weight_nan_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 10,
            "Prs_Weight": np.nan,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 1,
            "Prs_Weight": 10,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
    ])


def mock_avg_cycle_zero_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 0,
            "Prs_Weight": 0,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 0,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 1,
            "Prs_Weight": 10,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 30,
        },
    ])


def mock_avg_cycle_nan_data(extractor_cls, start_time, end_time, shift):
    return pd.DataFrame([
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 0,
            "Prs_Weight": 0,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": 0,
        },
        {
            "Shift_Start_Time": pd.Timestamp("2026-04-30 07:00:00"),
            "MachID": 1,
            "Style_Code": "A",
            "Weight": 1,
            "Prs_Weight": 10,
            "NAU_prs": 25,
            "ON_Time": 600,
            "OFF_Time": 300,
            "Avg_Cycle": np.nan,
        },
    ])