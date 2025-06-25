from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage
from config.llm_config import llm
from agents.preprocessor.df_inspector import inspect_df

def check_relevance(state):
    """
    Determine if the user's instruction is relevant and feasible for the DataFrame in state.data['df'].
    It returns a JSON dict with:
    - `is_relevant`: boolean indicating if the instruction is relevant
    - `issues`: null if relevant, or a string describing any issues if not.
    """
    # Inspect DataFrame context
    context = inspect_df(state).get("context", {})
    if not context:
        msg = "⚠️ No DataFrame found to check relevance against."
        state.data["parsed_relevance"] = {"is_relevant": False, "issues": msg}
        return {"messages": [AIMessage(content=msg)]}
    
    columns = context.get("columns", [])
    dtypes = context.get("dtypes", {})
    instruction = state.messages[-1].content

    # Construct system + human prompt for relevance
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a data preprocessing assistant. The user will give an instruction to modify a Pandas DataFrame `df`. "
                f"The DataFrame has these columns: {columns} with types: {dtypes}. "
                "Assess whether the instruction is relevant and feasible for this DataFrame. "
                "Return a JSON with `is_relevant` (bool) and `issues` (null or description)."
            )
        ),
        ("human", f"Instruction: {instruction}")
    ])

    # Invoke LLM and parse
    llm_response = llm.invoke(prompt)

    try:
        parsed = JsonOutputParser().parse(llm_response)
    except Exception as e:
        parsed = {"is_relevant": False, "issues": f"JSON parsing error: {e}"}

    # Store and acknowledge
    state.data["parsed_relevance"] = parsed
    summary = f"Relevance: {parsed['is_relevant']}."
    if parsed.get("issues"):
        summary += f" Issues: {parsed['issues']}"
    return {"messages": [AIMessage(content=summary)]}