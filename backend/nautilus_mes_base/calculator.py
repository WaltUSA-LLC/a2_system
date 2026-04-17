from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class WeightCalculator:
    def __init__(self, sku_weight: dict[str, float]) -> None:
        self.sku_weight = sku_weight

    @staticmethod
    def normalize_style(style_code: Any) -> str:
        if pd.isna(style_code):
            return ""
        style_code = style_code.strip()
        if len(style_code)==0:
            return ""
        style_code = style_code.upper()
        [style, size] = style_code.split()
        if '-' in style:
            style = style.split('-')[0]
        if 'CN' in style:
            style = style[:-2]
        #print(style+'-'+size)
        return style+'-'+size

    def estimate_prs_from_weight(self, rec: pd.Series) -> float:
        style = WeightCalculator.normalize_style(rec["Style_Code"])
        weight = rec["Weight"]

        if pd.isna(weight):
            return np.nan
        if weight == 0:
            return 0

        if style in self.sku_weight:
            prs_weight = self.sku_weight.get(style, np.nan) / 1000
            if prs_weight == 0 or pd.isna(prs_weight):
                return np.nan
            return weight // prs_weight
        return np.nan


    def append_weight_est(self, df: pd.DataFrame) -> pd.DataFrame:
        enriched = df.copy()
        enriched["Prs_Weight"] = enriched["Style_Code"].apply(lambda x: self.sku_weight.get(WeightCalculator.normalize_style(x),np.nan))
        enriched["MES_prs"] = enriched[["Style_Code", "Weight"]].apply(self.estimate_prs_from_weight, axis=1)
        return enriched

class TimeCalculator:
    @staticmethod
    def estimate_time_duration(t1:pd.Series, t2:pd.Series)->pd.Series:
        return (t2 - t1) / 60 # return duration minute