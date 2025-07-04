import uuid
from langchain_core.messages import AIMessage
from dataTools.sql_toolkit import make_sql_tools

# retrieve the full toolkit
_tools = make_sql_tools()

# pull in schema and query tools
_list_tables_tool = next(t for t in _tools if t.name == "sql_db_list_tables")

def list_tables(state):
    """
    Sub-agent: lists all tables in the SQL database.
    """
    call_id = str(uuid.uuid4())
    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": call_id,
        "type": "tool_call",
    }
    # Message to simulate tool invocation
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])

    # Invoke the actual tool
    tool_response = _list_tables_tool.invoke(tool_call)

    # Wrap and return
    response = AIMessage(f"Available tables: {tool_response.content}")
    return {"messages": [tool_call_message, tool_response, response]}