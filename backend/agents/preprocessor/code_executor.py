import pandas as pd
from langchain_core.messages import AIMessage
from agents.preprocessor.complexity_assessor import assess_complexity
from agents.preprocessor.df_inspector import inspect_df
from agents.state import AppState

def execute_code(state: AppState) -> AppState:
    """
    Execute the generated Python preprocessing code
    on the DataFrame.
    """
    df = state.retrieved_df
    code = state.generated_code
    
    if df is None:
        state.record_extra("execution_error", "Error: no DataFrame provided to execute code on.")
        state.set_apply_result(False)
        return state

    if not code:
        state.record_extra("execution_error", "Error: no code provided to execute.")
        state.set_apply_result(False)
        return state

    # Guard-rail check
    state = inspect_df(state)
    context = state.data.get("context", {})
    safe, warning = assess_complexity(code, context)
    if not safe:
        state.record_extra("execution_error", f"Unsafe code detected: {warning}")
        state.set_apply_result(False)
        return state

    # Execute the generated code in a controlled local environment
    local_env = {"df": df}
    try:
        exec(code, {}, local_env)
        new_df = local_env.get("df")
        # Validate output
        if not isinstance(new_df, pd.DataFrame):
            state.record_extra("execution_error", "Executed code did not yield a DataFrame named 'df'.")
            state.set_apply_result(False)
            return state
        
        # Update the state with the new DataFrame
        state.set_retrieved_df(new_df)
        state.set_apply_result(True)
        return state

    except Exception as e:
        state.record_extra("execution_error", f"Error executing preprocessing code: {e}")
        state.set_apply_result(False)
        return state
