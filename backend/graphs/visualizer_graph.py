from langgraph.graph import StateGraph, START, END
from agents.state import AppState
from agents.visualizer import (
    inspect_dataframe,
    check_feasibility,
    classify_visualization_type,
    prepare_visualization_data,
    generate_plots,
)

'''Flow diagram:
        START → inspect_dataframe → check_feasibility
                                         ├──[viz_feasible = True]──► classify_visualization_type → prepare_visualization_data → generate_plots → END
                                         └──[viz_feasible = False]─► END'''

def route_after_feasibility(state: AppState) -> str:
    """Determine if visualization should continue based on feasibility."""
    return "classify_visualization_type" if state.data.get("viz_feasible") else END


def build_visualizer_graph():
    """Build the visualizer graph following the same pattern as other agents."""
    builder = StateGraph(AppState)
    
    # Add visualizer sub-agent nodes (node_name first, then function)
    builder.add_node("inspect_dataframe", inspect_dataframe)
    builder.add_node("check_feasibility", check_feasibility)
    builder.add_node("classify_visualization_type", classify_visualization_type)
    builder.add_node("prepare_visualization_data", prepare_visualization_data)
    builder.add_node("generate_plots", generate_plots)
    
    # Wire the graph
    builder.add_edge(START, "inspect_dataframe")
    builder.add_edge("inspect_dataframe", "check_feasibility")
    
    # Only continue with visualization if feasible
    builder.add_conditional_edges(
        "check_feasibility",
        route_after_feasibility,
        {
            "classify_visualization_type": "classify_visualization_type",
            END: END
        }
    )
    
    # Continue with visualization pipeline
    builder.add_edge("classify_visualization_type", "prepare_visualization_data")
    builder.add_edge("prepare_visualization_data", "generate_plots")
    builder.add_edge("generate_plots", END)
    
    return builder.compile()
