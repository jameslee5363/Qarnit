from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from backend.config.llm_config import llm
from backend.agents.preprocessor.df_inspector import inspect_df
from backend.agents.state import AppState
import json

def suggest_preprocessing(state: AppState) -> AppState:
    """
    Suggest cleaning steps based on the DataFrame, using df_inspector for DRY context gathering.
    """
    # Gather context via the inspector
    #state = inspect_df(state)
    context = state.data.get("context", {})
    if not context:
        state.set_preprocessing_suggestion("Error: no context found to generate preprocessing suggestions.")
        return state

    # Extract context & prepare strings
    cols_str = ", ".join(context["columns"])
    dtypes_str = "\n".join(f"{col}: {dtype}" for col, dtype in context["dtypes"].items())
    sample_str = json.dumps(context["sample"], indent=2)

    # Build a clear system + human prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a data-cleaning expert. The user has a Pandas DataFrame in memory as `df`. "
                "Based on the columns and data types, suggest useful preprocessing steps "
                "(e.g., dropping nulls, normalizing values, encoding categories). "
                "Return a concise list of recommendations—no code."
            )
        ),
        (
            "human",
            "Columns: {cols_str}\nTypes: {dtypes_str}\nSample rows: {sample_str}\nWhat preprocessing steps do you suggest?"
        )
    ])

    formatted_prompt = prompt.format_messages(cols_str=cols_str, dtypes_str=dtypes_str, sample_str=sample_str)
    response = llm.invoke(formatted_prompt)
    
    # Update the state with the suggestion
    state.set_preprocessing_suggestion(str(response.content))
    return state