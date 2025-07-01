from typing import Dict, Any

def inspect_df(state) -> Dict[str, Any]:
    df = state.data.get("df")
    if df is None:
        return {"context": {}}
    return {"context": {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample": df.head(5).to_dict(orient='records'),
        "rows": len(df)
    }}