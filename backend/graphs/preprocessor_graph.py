from langgraph.graph import StateGraph, START, END
from agents.state import AppState
from agents.preprocessor import (
    inspect_df,
    suggest_preprocessing,
    check_relevance,
    generate_code,
    execute_code,
)

'''Flow diagram:
        START → inspect_df → suggest_preprocessing → check_relevance
                                                          ├──[is_relevant = True]──► generate_code → apply_preprocessing → END
                                                          └──[is_relevant = False]─► END'''

def build_preprocessor_graph():
    builder = StateGraph(AppState)
    
    # Add preprocessing sub-agent nodes (node_name first, then function)
    builder.add_node("inspect_df", inspect_df)
    builder.add_node("suggest_preprocessing", suggest_preprocessing)
    builder.add_node("check_relevance", check_relevance)
    builder.add_node("generate_code", generate_code)
    builder.add_node("apply_preprocessing", execute_code)
    
    # Wire the graph
    builder.add_edge(START, "inspect_df")
    builder.add_edge("inspect_df", "suggest_preprocessing")
    builder.add_edge("suggest_preprocessing", "check_relevance")
    
    # Only generate code if relevant, otherwise end
    builder.add_conditional_edges(
        "check_relevance",
        lambda state: "generate_code"
        if state.parsed_relevance and state.parsed_relevance.get("is_relevant")
        else END
    )
    
    # After code generation, apply it
    builder.add_edge("generate_code", "apply_preprocessing")
    builder.add_edge("apply_preprocessing", END)
    
    return builder.compile()