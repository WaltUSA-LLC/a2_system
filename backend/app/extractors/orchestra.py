from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd

from sqlalchemy import create_engine
from extractors.query import MES_QUERY, STOP_QUERY

from extractors.calculator import WeightCalculator, TimeCalculator
from extractors.cleaner import WeightCleaner
from extractors.config import AppConfig
from extractors.repositories import DataRepository, WeightRepository
from extractors.writers import ExcelWriter


class MESOrchestra:
    def __init__(
        self,
        repository: DataRepository,
        cleaner: WeightCleaner,
        calculator: WeightCalculator,
        writer: ExcelWriter,
        data_log: bool,
    ) -> None:
        self.repository = repository
        self.cleaner = cleaner
        self.calculator = calculator
        self.writer = writer
        self.data_log = data_log

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESOrchestra":
        engine = create_engine(config.database_url)
        mes_data = DataRepository(engine, MES_QUERY)
        cleaner = WeightCleaner()
        weights = WeightRepository(config.weights_path).get_weights()
        calculator = WeightCalculator(weights)
        writer = ExcelWriter(config.output_dir, "MES_DATA", "mes_base")
        return cls(mes_data, cleaner, calculator, writer, config.data_log)

    def generate_mes(self, start_dt: datetime, end_dt: datetime, shift: int) -> pd.DataFrame:
        dfs = []
        current_dt = start_dt
        while current_dt <= end_dt:
            if shift!=0:
                df = self.repository.fetch_data_with_start_date(current_dt, shift)
                df = self.cleaner.clean(df)
                df = self.calculator.append_weight_est(df)
                dfs.append(df)
                print(f"finished mes {current_dt} shift {shift}")
            else:
                for shift_iter in range(1, 3):
                    df = self.repository.fetch_data_with_start_date(current_dt, shift_iter)
                    df = self.cleaner.clean(df)
                    df = self.calculator.append_weight_est(df)
                    dfs.append(df)
                    print(f"finished mes {current_dt} shift {shift_iter}")
            current_dt += timedelta(days=1)
        all_df = pd.concat(dfs, ignore_index=True)
        if self.data_log:
            self.writer.to_excel(all_df, start_dt, end_dt)
        all_df.drop(columns=["Prs_Weight"], inplace=True) 
        return all_df
    
    
class NAUStopOrchestra:
    def __init__(
        self,
        repository: DataRepository,
        writer: ExcelWriter,
        data_log: bool,
    ) -> None:
        self.repository = repository
        self.writer = writer
        self.data_log = data_log

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESOrchestra":
        engine = create_engine(config.database_url)
        nau_run_data = DataRepository(engine, STOP_QUERY)
        writer = ExcelWriter(config.output_dir, "NAU_STOP_DATA", "nau_stop")
        return cls(nau_run_data, writer, config.data_log)

    def generate_nau_stop(self, start_dt: datetime, end_dt: datetime) -> list[str]:
        df = self.repository.fetch_data_with_start_end_date(start_dt, end_dt + timedelta(days=1))
        print(f"finished sql query with {len(df)}")
        df["dur_minute"] = TimeCalculator.estimate_time_duration(df["Stop_time"], df["Recover_time"])
        #df = df.sort_values(by=["MachID", "dur_minute"], ascending=[True, False])
        print(f"finished df process")
        if self.data_log:
            self.writer.to_excel(df, start_dt, end_dt)
        return df
