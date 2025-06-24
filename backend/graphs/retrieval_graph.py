

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END, MessagesState
from agents.retriever import (
    list_tables, call_get_schema, generate_query, check_query, should_continue
)
from database.sql_toolkit import make_sql_tools


def build_retriever_agent_graph():
    tools = make_sql_tools()
    get_schema_tool = next(t for t in tools if t.name == "sql_db_schema")
    run_query_tool = next(t for t in tools if t.name == "sql_db_query")

    get_schema_node = ToolNode([get_schema_tool], name="get_schema")
    run_query_node = ToolNode([run_query_tool], name="run_query")

    builder = StateGraph(MessagesState)
    builder.add_node(list_tables)
    builder.add_node(call_get_schema)
    builder.add_node(get_schema_node, "get_schema")
    builder.add_node(generate_query)
    builder.add_node(check_query)
    builder.add_node(run_query_node, "run_query")

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges(
        "generate_query", 
        should_continue
    )
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    # Ensure a path to END if no tool calls remain
    # builder.add_edge("generate_query", END)

    return builder.compile()