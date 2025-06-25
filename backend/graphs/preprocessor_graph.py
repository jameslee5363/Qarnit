from langgraph.graph import StateGraph, START, END, MessagesState
from agents.preprocessor import (
    inspect_df,
    suggest_preprocessing,
    check_relevance,
    generate_code,
    execute_code,
)

def build_preprocessor_graph():
    builder = StateGraph(MessagesState)
    # Add sentinel nodes
    builder.add_node(START)
    builder.add_node(END)

    # Add preprocessing sub-agent nodes
    builder.add_node(inspect_df,            "inspect_df")
    builder.add_node(suggest_preprocessing, "suggest_preprocessing")
    builder.add_node(check_relevance,       "check_relevance")
    builder.add_node(generate_code,         "generate_code")
    builder.add_node(execute_code,   "apply_preprocessing")

    # Wire the graph
    builder.add_edge(START,  "inspect_df")
    builder.add_edge("inspect_df", "suggest_preprocessing")
    builder.add_edge("suggest_preprocessing", "check_relevance")

    # Only generate code if relevant, otherwise end
    builder.add_conditional_edges(
        "check_relevance",
        lambda state: "generate_code"
        if state.data.get("parsed_relevance", {}).get("is_relevant")
        else END
    )

    # After code generation, apply it
    builder.add_edge("generate_code",       "apply_preprocessing")
    builder.add_edge("apply_preprocessing", END)

    return builder.compile()