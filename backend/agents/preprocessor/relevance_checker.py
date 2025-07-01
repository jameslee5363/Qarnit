import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage
from config.llm_config import llm
from agents.preprocessor.df_inspector import inspect_df

def check_relevance(user_instruction, df):
    """
    Determine if the user's instruction is relevant and feasible for the DataFrame.
    It returns a JSON dict with:
    - `is_relevant`: boolean indicating if the instruction is relevant
    - `issues`: null if relevant, or a string describing any issues if not.
    """
    # Inspect DataFrame context
    context = inspect_df(df).get("context", {})
    if not context:
        return {
            "is_relevant": False,
            "issues": "⚠️ No DataFrame provided to check relevance against."
        }

    # Extract context & prepare strings
    cols_str = ", ".join(context["columns"])
    dtypes_str = "\n".join(f"{col}: {dtype}" for col, dtype in context["dtypes"].items())
    sample_str = json.dumps(context["sample"], indent=2)

    # Construct system + human prompt for relevance
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a data preprocessing assistant. The user will give an instruction to modify a Pandas DataFrame `df`. "
                "The DataFrame has these columns: {cols_str} with types: {dtypes_str} and sample rows: {sample_str}."
                "Assess whether the instruction is relevant and feasible for this DataFrame. "
                "Return a JSON with `is_relevant` (bool) and `issues` (null or description)."
            )
        ),
        ("human", "Instruction: {user_instruction}")
    ])

    # Invoke LLM and parse
    formatted_prompt = prompt.format_messages(cols_str=cols_str, dtypes_str=dtypes_str, sample_str=sample_str, user_instruction=user_instruction)
    response = llm.invoke(formatted_prompt)

    try:
        parsed = JsonOutputParser().parse(str(response.content))
    except Exception as e:
        parsed = {"is_relevant": False, "issues": f"JSON parsing error: {e}"}

    return parsed