import pandas as pd
from langchain_core.messages import AIMessage

def execute_code(state):
    """
    Execute the generated Python preprocessing code from state.data['generated_code']
    on the DataFrame stored in state.data['df'], then update state.data['df'].
    Returns an AIMessage confirming success or reporting errors.
    """
    df = state.data.get("df")
    code = state.data.get("generated_code")

    if df is None:
        return {"messages": [AIMessage(content="⚠️ No DataFrame available for preprocessing.")]}

    if not code:
        return {"messages": [AIMessage(content="⚠️ No preprocessing code found to apply.")]}

    # Execute the generated code in a controlled local environment
    local_env = {"df": df}
    try:
        exec(code, {}, local_env)
        new_df = local_env.get("df")
        if not isinstance(new_df, pd.DataFrame):
            raise RuntimeError("Executed code did not return a DataFrame named 'df'.")
        # Update state with the new DataFrame
        state.data["df"] = new_df
        return {"messages": [AIMessage(content="✅ Successfully applied preprocessing code.")]}
    except Exception as e:
        return {"messages": [AIMessage(content=f"❌ Error executing preprocessing code: {e}")]}





