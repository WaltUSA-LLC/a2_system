import math
import pandas as pd
import numpy as np

def validate_throughput(rec:pd.Series) -> pd.Series:
    nau = rec["NAU_prs"]
    weight = rec["MES_prs"]
    on_time = rec["ON_Time"]
    avg_cycle = rec["Avg_Cycle"]
    discard = rec["Discard_prs"]
    theory_expect = math.ceil(on_time/avg_cycle/2) if not pd.isna(avg_cycle) else np.nan
    act_expect = theory_expect - discard if not pd.isna(theory_expect) else np.nan
    buffer = 10
    
    if (nau==0 and on_time==0) or (weight==0 and on_time==0):
        return 0
    if (weight<0 or weight>theory_expect+buffer or pd.isna(weight)) and (nau<0 or nau>theory_expect+buffer or pd.isna(nau)):
        return np.nan
    elif (weight<0 or weight>theory_expect+buffer or pd.isna(weight)):
        return nau
    else:
        return weight
    
    
def estimate_st_output_prs(rec: pd.Series) -> int:
    if pd.isna(rec["Avg_Cycle"]):
        return np.nan
    return math.floor((rec["ON_Time"]+rec["OFF_Time"])/rec["Avg_Cycle"]/2)