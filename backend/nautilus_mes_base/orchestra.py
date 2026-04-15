from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd

from sqlalchemy import create_engine
from nautilus_mes_base.query import MES_QUERY, NAU_RUN_TIME_QUERY, NAU_STOP_QUERY

from nautilus_mes_base.calculator import WeightCalculator, TimeCalculator
from nautilus_mes_base.cleaner import WeightCleaner
from nautilus_mes_base.config import AppConfig
from nautilus_mes_base.repositories import DataRepository, WeightRepository
from nautilus_mes_base.writers import ExcelWriter


class MESOrchestra:
    def __init__(
        self,
        repository: DataRepository,
        cleaner: WeightCleaner,
        calculator: WeightCalculator,
        writer: ExcelWriter,
    ) -> None:
        self.repository = repository
        self.cleaner = cleaner
        self.calculator = calculator
        self.writer = writer

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESOrchestra":
        engine = create_engine(config.database_url)
        mes_data = DataRepository(engine, MES_QUERY)
        cleaner = WeightCleaner()
        weights = WeightRepository(config.weights_path).get_weights()
        calculator = WeightCalculator(weights)
        writer = ExcelWriter(config.output_dir, "MES_DATA", "mes_base")
        return cls(mes_data, cleaner, calculator, writer)

    def generate_mes(self, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
        dfs = []
        current_dt = start_dt
        while current_dt <= end_dt:
            for shift in range(1, 3):
                df = self.repository.fetch_shift_data(current_dt, shift)
                df = self.cleaner.clean(df)
                df = self.calculator.append_weight_est(df)
                dfs.append(df)
                print(f"finished mes {current_dt} shift {shift}")
            current_dt += timedelta(days=1)
        all_df = pd.concat(dfs, ignore_index=True)
        all_df.drop(columns=["Prs_Weight"], inplace=True)
        #output_path = self.writer.to_excel(all_df, start_dt, end_dt)
        return all_df

class NAUTimeOrchestra:
    def __init__(
        self,
        repository: DataRepository,
        writer: ExcelWriter,
    ) -> None:
        self.repository = repository
        self.writer = writer

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESOrchestra":
        engine = create_engine(config.database_url)
        nau_run_data = DataRepository(engine, NAU_RUN_TIME_QUERY)
        writer = ExcelWriter(config.output_dir, "NAU_TIME_DATA", "nau_run")
        return cls(nau_run_data, writer)

    def generate_nau_time(self, start_dt: datetime, end_dt: datetime) -> list[str]:
        dfs = []
        current_dt = start_dt
        while current_dt <= end_dt:
            df = self.repository.fetch_shift_data(current_dt)
            dfs.append(df)
            print(f"finished nau time {current_dt}")
            current_dt += timedelta(days=1)
        all_df = pd.concat(dfs, ignore_index=True)
        #output_path = self.writer.to_excel(all_df, start_dt, end_dt)
        return all_df
    
class NAUStopOrchestra:
    def __init__(
        self,
        repository: DataRepository,
        writer: ExcelWriter,
    ) -> None:
        self.repository = repository
        self.writer = writer

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESOrchestra":
        engine = create_engine(config.database_url)
        nau_run_data = DataRepository(engine, NAU_STOP_QUERY)
        writer = ExcelWriter(config.output_dir, "NAU_STOP_DATA", "nau_stop")
        return cls(nau_run_data, writer)

    def generate_nau_stop(self, start_dt: datetime, end_dt: datetime) -> list[str]:
        dfs = []
        current_dt = start_dt
        while current_dt <= end_dt:
            df = self.repository.fetch_shift_data(current_dt)
            df["dur_minute"] = TimeCalculator.estimate_time_duration(df["Stop_time"], df["Recover_time"])
            df = df.sort_values(by=["MachID", "dur_minute"], ascending=[True, False])
            dfs.append(df)
            print(f"finished nau stop {current_dt}")
            current_dt += timedelta(days=1)
        all_df = pd.concat(dfs, ignore_index=True)
        #output_path = self.writer.to_excel(all_df, start_dt, end_dt)
        return all_df