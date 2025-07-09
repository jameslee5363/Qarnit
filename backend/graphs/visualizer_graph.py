from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from agents.visualizer import (
    inspect_data,
    select_visualization_types,
    check_feasibility,
    prepare_visualization_data,
    generate_plots,
    validate_plots,
)


class VisualizerState(TypedDict):
    """Custom state for visualizer graph that includes both messages and custom fields."""
    messages: List[BaseMessage]
    retrieved_df: Optional[Any]
    initial_question: Optional[str]
    data_description: Optional[str]
    visualization_types: Optional[List[str]]
    viz_feasibility: Optional[bool]
    feasibility_details: Optional[Dict[str, Any]]
    prepared_viz_data: Optional[Dict[str, Any]]
    generated_plots: Optional[Dict[str, Any]]
    plot_validation_results: Optional[Dict[str, Any]]
    visualization_complete: Optional[bool]


def route_after_feasibility(state: VisualizerState) -> str:
    """Determine if visualization should continue based on feasibility."""
    return "prepare_visualization_data" if state.get("viz_feasibility") else END


def build_visualizer_graph():
    """Build the visualizer graph with proper state management and flow control."""
    builder = StateGraph(VisualizerState)
    
    # Add visualizer sub-agent nodes
    builder.add_node("inspect_data", inspect_data)
    builder.add_node("select_visualization_types", select_visualization_types)
    builder.add_node("check_feasibility", check_feasibility)
    builder.add_node("prepare_visualization_data", prepare_visualization_data)
    builder.add_node("generate_plots", generate_plots)
    builder.add_node("validate_plots", validate_plots)
    
    # Wire the graph
    builder.add_edge(START, "inspect_data")
    builder.add_edge("inspect_data", "select_visualization_types")
    builder.add_edge("select_visualization_types", "check_feasibility")
    
    # Conditional routing based on feasibility
    builder.add_conditional_edges(
        "check_feasibility",
        route_after_feasibility,
        {
            "prepare_visualization_data": "prepare_visualization_data",
            END: END
        }
    )
    
    # Continue with visualization pipeline
    builder.add_edge("prepare_visualization_data", "generate_plots")
    builder.add_edge("generate_plots", "validate_plots")
    builder.add_edge("validate_plots", END)
    
    return builder.compile()
