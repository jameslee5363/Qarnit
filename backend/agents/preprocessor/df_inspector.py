import pandas as pd

def inspect_df(df):
    if df is None:
        return {"context": {}}

    # Basic schema info
    columns = df.columns.tolist()
    dtypes = df.dtypes.apply(lambda dt: dt.name).to_dict()
    rows = len(df)
    sample = df.head(3).to_dict(orient="records")

    # Cardinality for each categorical/text column
    cardinalities = {
        col: int(df[col].nunique())
        for col in df.select_dtypes(include=["object", "category"]).columns
    }

    return {
        "context": {
            "columns": columns,
            "dtypes": dtypes,
            "rows": rows,
            "sample": sample,
            "cardinalities": cardinalities,
        }
    }