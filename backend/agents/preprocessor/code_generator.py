from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import llm
from agents.preprocessor.df_inspector import inspect_df

def generate_code(state):
    """
    Generate Python pandas code to implement the user's preprocessing instruction.
    - Expects the DataFrame in state.data['df'].
    - Uses df_inspector for context (columns, types, sample).
    - Stores the raw code in state.data['generated_code'].
    Returns a confirmation AIMessage.
    """
    # Retrieve DataFrame
    df = state.data.get("df")
    if df is None:
        msg = "⚠️ No DataFrame found to generate code for."
        state.data["generated_code"] = None
        return {"messages": [AIMessage(content=msg)]}

    # Gather context
    context = inspect_df(state).get("context", {})
    columns = context.get("columns", [])
    dtypes = context.get("dtypes", {})
    sample = context.get("sample", [])

    instruction = state.messages[-1].content

    # Build prompt for code generation
    system_prompt = (
        "You are a Python pandas expert. You have a DataFrame `df` with:\n"
        f"  • columns: {columns}\n"
        f"  • types: {dtypes}\n"
        f"  • sample rows: {sample}\n\n"
        f"The user instruction is: \"{instruction}\".\n"
        "Generate valid Python pandas code that modifies `df` accordingly. "
        "Return **only** the code block—no explanation."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Please provide the Python code:")
    ])

    # Invoke LLM and extract code
    response = llm.invoke(prompt).strip()
    # Strip any markdown fences
    code = response.strip("```").strip()

    # Save and confirm
    state.data["generated_code"] = code
    return {"messages": [AIMessage(content="✅ Generated python code.")]}
