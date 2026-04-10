from __future__ import annotations

import pandas as pd


class WeightCleaner:
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned_df = df.copy()
        if "Weight" in cleaned_df.columns:
            mask = (cleaned_df["Weight"] > 0) & (cleaned_df["Weight"] < 1)
            cleaned_df.loc[mask, "Weight"] = 0
        return cleaned_df