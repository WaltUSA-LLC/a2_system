from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from extractors.query import MES_QUERY, STOP_QUERY

from extractors.calculator import WeightCalculator, TimeCalculator
from extractors.cleaner import WeightCleaner
from extractors.config import AppConfig
from extractors.repositories import DataRepository, WeightRepository
from extractors.writers import ExcelWriter

class BaseExtractor(ABC):
    def __init__(
        self,
        repository: DataRepository,
        writer: ExcelWriter,
        log_data_output: bool,
    ) -> None:
        self.repository = repository
        self.writer = writer
        self.log_data_output = log_data_output

    @classmethod
    @abstractmethod
    def from_config(cls, config: AppConfig) -> "BaseExtractor":
        pass

    @abstractmethod
    def extract(self, start_dt: datetime, end_dt: datetime, *args, **kwargs) -> pd.DataFrame:
        pass


class MESExtractor(BaseExtractor):
    def __init__(
        self,
        repository: DataRepository,
        calculator: WeightCalculator,
        writer: ExcelWriter,
        log_data_output: bool,
    ) -> None:
        self.repository = repository
        self.calculator = calculator
        self.writer = writer
        self.log_data_output = log_data_output

    @classmethod
    def from_config(cls, config: AppConfig) -> "MESExtractor":
        engine = create_engine(config.database_url)
        mes_data = DataRepository(engine, MES_QUERY)
        weights = WeightRepository(config.weights_path).get_weights()
        calculator = WeightCalculator(weights)
        writer = ExcelWriter(config.output_dir, "MES_DATA", "mes_base")
        return cls(mes_data, calculator, writer, config.log_data_output)

    def extract(self, start_dt: datetime, end_dt: datetime, shift: int) -> pd.DataFrame:
        dfs = []
        current_dt = start_dt
        while current_dt <= end_dt:
            if shift!=0:
                df = self.repository.fetch_data_with_start_date(current_dt, shift)
                df = self.calculator.append_weight_est(df)
                dfs.append(df)
                print(f"finished mes {current_dt} shift {shift}")
            else:
                for shift_iter in range(1, 3):
                    df = self.repository.fetch_data_with_start_date(current_dt, shift_iter)
                    df = self.calculator.append_weight_est(df)
                    dfs.append(df)
                    print(f"finished mes {current_dt} shift {shift_iter}")
            current_dt += timedelta(days=1)
        all_df = pd.concat(dfs, ignore_index=True)
        if self.log_data_output:
            self.writer.to_excel(all_df, start_dt, end_dt, shift)
        all_df.drop(columns=["Prs_Weight"], inplace=True) 
        return all_df
    
    
class StopExtractor(BaseExtractor):
    def __init__(
        self,
        repository: DataRepository,
        writer: ExcelWriter,
        log_data_output: bool,
    ) -> None:
        self.repository = repository
        self.writer = writer
        self.log_data_output = log_data_output

    @classmethod
    def from_config(cls, config: AppConfig) -> "StopExtractor":
        engine = create_engine(config.database_url)
        nau_run_data = DataRepository(engine, STOP_QUERY)
        writer = ExcelWriter(config.output_dir, "STOP_DATA", "stop")
        return cls(nau_run_data, writer, config.log_data_output)

    def extract(self, start_dt: datetime, end_dt: datetime, shift:int) -> list[str]:
        df = self.repository.fetch_data_with_start_end_date(start_dt, end_dt + timedelta(days=1))
        print(f"finished sql query with {len(df)}")
        df["dur_minute"] = TimeCalculator.estimate_time_duration(df["Stop_time"], df["Recover_time"])
        #df = df.sort_values(by=["MachID", "dur_minute"], ascending=[True, False])
        print(f"finished df process")
        if self.log_data_output:
            self.writer.to_excel(df, start_dt, end_dt)
        return df