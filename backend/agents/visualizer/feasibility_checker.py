from langchain_core.messages import AIMessage

def check_feasibility(state):
    df = state.data.get("df")
    if df is None or df.shape[0] < 2:
        return {"messages": [AIMessage(content="⚠️ DataFrame too small to visualize.")],
                "data": {"feasible": False}}
    cols = df.select_dtypes(include=["number","object","category"]).columns
    if cols.empty:
        return {"messages": [AIMessage(content="⚠️ No plottable columns.")],
                "data": {"feasible": False}}
    return {"data": {"feasible": True}}