import json
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import llm
from agents.preprocessor.df_inspector import inspect_df

def generate_code(df, user_instruction):
    """
    Generate Python pandas code to implement the user's preprocessing instruction.
    - Expects the DataFrame.
    - Uses df_inspector for context (columns, types, sample).
    - Stores the raw code in state.data['generated_code'].
    Returns a confirmation AIMessage.
    """
    # Gather context via the inspector
    context = inspect_df(df).get("context", {})
    if not context:
        return "Error: no context found to generate preprocessing suggestions."

    # Extract context & prepare strings
    cols_str = ", ".join(context["columns"])
    dtypes_str = "\n".join(f"{col}: {dtype}" for col, dtype in context["dtypes"].items())
    sample_str = json.dumps(context["sample"], indent=2)
    cardinalities = "\n".join(f"{col}: {dtype}" for col, dtype in context["cardinalities"].items())

    # Build prompt for code generation
    system_prompt = (
        "You are a Python pandas expert. You have a DataFrame `df` with:\n"
        "columns: {cols_str}\n"
        "types: {dtypes_str}\n"
        "sample rows: {sample_str}\n\n"
        "Cardinalities: {cardinalities}\n\n"
        "The user instruction is: \"{user_instruction}\".\n"
        "If any column’s cardinality exceeds 100 and you would normally one-hot encode it, "
        "instead include a comment suggesting a more memory-efficient approach "
        "(e.g., feature hashing or sparse encoding). "
        "Generate valid Python pandas code that modifies `df` accordingly. "
        "Return **only** the code block— no explanation, no markdown fences, no comments."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Please provide the Python code:")
    ])

    # Invoke LLM and extract code
    formatted_prompt = prompt.format_messages(cols_str=cols_str, dtypes_str=dtypes_str, sample_str=sample_str, user_instruction=user_instruction)
    response = llm.invoke(formatted_prompt)
    # Strip any markdown fences
    #code = response.strip("```").strip()


    return response.content
