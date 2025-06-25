from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import llm
from agents.preprocessor.df_inspector import inspect_df

def suggest_preprocessing(state):
    """
    Suggest cleaning steps based on the DataFrame in state.data['df'], 
    using df_inspector for DRY context gathering.
    """
    # Gather context via the inspector
    context = inspect_df(state).get("context", {})
    if not context:
        return {"messages": [AIMessage(content="⚠️ No DataFrame to preprocess.")]}

    columns = context["columns"]
    dtypes = context["dtypes"]
    sample = context["sample"]

    # Prepare strings and escape braces for the prompt
    dtypes_str = str(dtypes).replace("{", "{{").replace("}", "}}")
    sample_str = str(sample).replace("{", "{{").replace("}", "}}")

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
            f"Columns: {columns}\nTypes: {dtypes_str}\nSample rows: {sample_str}\nWhat preprocessing steps do you suggest?"
        )
    ])

    response = llm.invoke(prompt)
    return {"messages": [AIMessage(content=response.strip())]}