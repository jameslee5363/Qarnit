"""
Feasibility Checker for Visualizer Agent
Determines if DataFrame is suitable for visualization.
"""

import pandas as pd
from agents.state import AppState


def check_feasibility(state: AppState) -> AppState:
    """
    Check if the DataFrame in state can be visualized.
    Sets feasibility flag and reasoning in state.
    """
    df = state.data.get("df")
    
    if df is None:
        state.data["viz_feasible"] = False
        state.data["feasibility_reason"] = "No DataFrame found"
        return state
    
    # Check basic requirements
    if df.shape[0] < 2:
        state.data["viz_feasible"] = False
        state.data["feasibility_reason"] = f"Insufficient data: only {df.shape[0]} rows"
        return state
    
    # Check for visualizable columns
    viz_cols = df.select_dtypes(include=["number", "object", "category"]).columns
    if viz_cols.empty:
        state.data["viz_feasible"] = False
        state.data["feasibility_reason"] = "No numeric or categorical columns for visualization"
        return state
    
    # Passed all checks
    state.data["viz_feasible"] = True
    state.data["feasibility_reason"] = f"Ready for visualization: {len(viz_cols)} suitable columns"
    
    return state


def is_feasible(df: pd.DataFrame) -> bool:
    """
    Simple boolean check for DataFrame visualization feasibility.
    Utility function for direct DataFrame checking.
    """
    if df is None or df.shape[0] < 2:
        return False
    viz_cols = df.select_dtypes(include=["number", "object", "category"]).columns
    return not viz_cols.empty