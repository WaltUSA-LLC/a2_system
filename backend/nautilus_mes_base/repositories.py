from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


class WeightRepository:
    def __init__(self, weights_path: Path) -> None:
        self.weights_path = weights_path
        self._cache: dict[str, float] | None = None

    def get_weights(self) -> dict[str, float]:
        if self._cache is None:
            with open(self.weights_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
        return self._cache


class DataRepository:
    def __init__(self, engine: Engine, query: str) -> None:
        self.engine = engine
        self.query = query

    def fetch_shift_data(self, start_dt: datetime, shift: int) -> pd.DataFrame:
        params = {"start_dt": start_dt, "shift": shift}
        return pd.read_sql_query(text(self.query), con=self.engine, params=params)
