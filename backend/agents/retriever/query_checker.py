from typing import Literal
from langchain_core.messages import AIMessage
from backend.dataTools.sql_toolkit import make_sql_tools
from langgraph.graph import END
from backend.config.llm_config import llm
from backend.config.db_config import db

# prompt for checking queries
_check_query_system_prompt = f"""
You are a SQL expert—double check the {db.dialect} query for common mistakes:
- NOT IN with NULLs
- UNION vs UNION ALL
- BETWEEN ranges
- Data-type mismatches
- Quoting identifiers, etc.
If mistakes exist, rewrite; otherwise reproduce the query.
"""

# pull in run_query tool
_tools = make_sql_tools()
_run_query_tool = next(t for t in _tools if t.name == "sql_db_query")


def check_query(state) -> dict[str, list[AIMessage]]:
    """
    Sub-agent: validates and optionally rewrites the SQL query before execution.
    """
    # build system/user messages for the checker
    system_message = {"role": "system", "content": _check_query_system_prompt}
    last_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": last_call["args"]["query"]}

    llm_with_tools = llm.bind_tools([_run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])
    # preserve the original message ID
    response.id = state["messages"][-1].id
    return {"messages": [response]}

def should_continue(state) -> Literal["__end__", "check_query"]:
    """Determines whether to re-enter the check_query step or finish."""
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return "__end__"
    return "check_query"