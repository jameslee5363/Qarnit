def inspect_df(state):
    df = state.data.get("df")
    if df is None:
        return {"context": {}}
    return {
      "context": {
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "rows": len(df),
        "sample": df.head(3).to_dict(orient="records"),
      }
    }