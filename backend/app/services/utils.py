import math
import pandas as pd
import numpy as np


def estimate_st_output_prs(rec: pd.Series) -> int:
    if pd.isna(rec["Avg_Cycle"]):
        return np.nan
    return math.floor((rec["ON_Time"]+rec["OFF_Time"])/rec["Avg_Cycle"]/2)