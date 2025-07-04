from langchain_core.messages import AIMessage
import pandas as pd

def check_feasibility(df: pd.DataFrame) -> bool:
    # Need at least 2 rows and ≥1 numeric or categorical column
    if df is None or df.shape[0] < 2 :
        return False
    cols = df.select_dtypes(include=["number","object","category"]).columns
    return not cols.empty