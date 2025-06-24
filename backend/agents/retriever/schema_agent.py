from langchain_core.messages import AIMessage
from database.sql_toolkit import make_sql_tools
from config.llm_config import llm

# pull in schema and query tools
_tools = make_sql_tools()
_get_schema_tool = next(t for t in _tools if t.name == "sql_db_schema")


def call_get_schema(state):
    """
    Sub-agent: lets the LLM generate and execute a schema tool call.
    """
    # bind only the schema tool
    llm_with_tools = llm.bind_tools([_get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}