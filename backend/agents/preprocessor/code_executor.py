import pandas as pd
from langchain_core.messages import AIMessage
from agents.preprocessor.complexity_assessor import assess_complexity
from agents.preprocessor.df_inspector import inspect_df

def execute_code(df, code):
    """
    Execute the generated Python preprocessing code
    on the DataFrame.
    """
    if df is None:
        return "Error: no DataFrame provided to execute code on."

    if not code:
        return "Error: no code provided to execute."

    # Guard-rail check
    context = inspect_df(df).get("context", {})
    safe, warning = assess_complexity(code, context)
    if not safe:
        return {"df": None, "error": f"Unsafe code detected: {warning}"}

    # Execute the generated code in a controlled local environment
    local_env = {"df": df}
    try:
        exec(code, {}, local_env)
        new_df = local_env.get("df")
        # Validate output
        if not isinstance(new_df, pd.DataFrame):
            return {
                "df": None,
                "error": "Executed code did not yield a DataFrame named 'df'."
            }
        return {"df": new_df, "error": None}

    except Exception as e:
        return {"df": None, "error": f"Error executing preprocessing code: {e}"}
