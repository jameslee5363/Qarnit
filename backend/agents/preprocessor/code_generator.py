import json
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from backend.config.llm_config import llm
from backend.agents.preprocessor.df_inspector import inspect_df
from backend.agents.state import AppState

def generate_code(state: AppState) -> AppState:
    """
    Generate Python pandas code to implement the user's preprocessing instruction.
    - Expects the DataFrame.
    - Uses df_inspector for context (columns, types, sample).
    - Stores the raw code in state.data['generated_code'].
    Returns a confirmation AIMessage.
    """
    # Get user instruction from state
    user_instruction = state.preprocessing_instruction
    
    # Gather context via the inspector
    #state = inspect_df(state)
    context = state.data.get("context", {})
    if not context:
        state.set_generated_code("Error: no context found to generate preprocessing suggestions.")
        return state

    # Extract context & prepare strings
    cols_str = ", ".join(context["columns"])
    dtypes_str = "\n".join(f"{col}: {dtype}" for col, dtype in context["dtypes"].items())
    sample_str = json.dumps(context["sample"], indent=2)
    
    # Handle cardinalities safely
    cardinalities = context.get("cardinalities", {})
    if cardinalities:
        cardinalities_str = "\n".join(f"{col}: {dtype}" for col, dtype in cardinalities.items())
    else:
        cardinalities_str = "No categorical columns found"

    # Build prompt for code generation
    system_prompt = (
        "You are a Python pandas expert. You have a DataFrame `df` with:\n"
        "columns: {cols_str}\n"
        "types: {dtypes_str}\n"
        "sample rows: {sample_str}\n\n"
        "Cardinalities: {cardinalities_str}\n\n"
        "The user instruction is: \"{user_instruction}\".\n"
        "If any column's cardinality exceeds 100 and you would normally one-hot encode it, "
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
    formatted_prompt = prompt.format_messages(cols_str=cols_str, dtypes_str=dtypes_str, sample_str=sample_str, user_instruction=user_instruction, cardinalities_str=cardinalities_str)
    response = llm.invoke(formatted_prompt)
    # Strip any markdown fences
    #code = response.strip("```").strip()

    # Update the state with the generated code
    state.set_generated_code(response.content)
    return state
