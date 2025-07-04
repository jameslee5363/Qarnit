from typing import Dict, Any
import pandas as pd

def inspect_df(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample": df.head(5).to_dict(orient="records"),
        "rows": len(df),
    }