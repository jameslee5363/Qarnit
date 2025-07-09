from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END, MessagesState
from backend.agents.retriever import (
    list_tables, call_get_schema, generate_query, check_query, should_continue
)
from backend.dataTools.sql_toolkit import make_sql_tools

'''Flow diagram:
        START → list_tables → call_get_schema → get_schema (tool)
            → generate_query ──┬──[END if no tool calls]──────────────► END
                               └── check_query → run_query (tool) ─┐
                                                                   └──────────► generate_query (loop)'''

def build_retriever_graph():
    tools = make_sql_tools()
    get_schema_tool = next(t for t in tools if t.name == "sql_db_schema")
    run_query_tool = next(t for t in tools if t.name == "sql_db_query")

    get_schema_node = ToolNode([get_schema_tool])
    run_query_node = ToolNode([run_query_tool])

    builder = StateGraph(MessagesState)
    
    # Add nodes with correct parameter order (name first, then function/node)
    builder.add_node("list_tables", list_tables)
    builder.add_node("call_get_schema", call_get_schema)
    builder.add_node("get_schema", get_schema_node)
    builder.add_node("generate_query", generate_query)
    builder.add_node("check_query", check_query)
    builder.add_node("run_query", run_query_node)

    # Wire the graph
    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    
    # Conditional edges from generate_query
    builder.add_conditional_edges(
    "generate_query", 
    should_continue,
    {
        "check_query": "check_query",
        "__end__": END
    }
    )
    
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    return builder.compile()