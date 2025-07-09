"""
Data Preparer for Visualizer Agent
Prepares DataFrame and parameters for specific visualization types.
"""

import pandas as pd
from typing import Dict, Any
from agents.state import AppState
from visualization_classifier import parse_viz_types


def prepare_visualization_data(state: AppState) -> AppState:
    """
    Prepare data for visualization based on recommended types.
    Expects recommended_viz_types to be set by visualization_classifier.
    """
    df = state.data.get("df")
    viz_context = state.data.get("viz_context", {})
    viz_types = viz_context.get("recommended_viz_types", [])
    
    if df is None:
        state.set_error("No DataFrame found for visualization preparation")
        return state
        
    if not viz_types:
        state.set_error("No visualization types recommended. Run classifier first.")
        return state
    
    # Prepare data for each visualization type
    prepared_data = {}
    
    for viz_type in viz_types:
        try:
            if viz_type == "bar_graph":
                data = _prepare_bar_graph(df)
            elif viz_type == "line_graph":
                data = _prepare_line_graph(df)
            elif viz_type == "histogram":
                data = _prepare_histogram(df)
            elif viz_type == "box_plot":
                data = _prepare_box_plot(df)
            elif viz_type == "scatter":
                data = _prepare_scatter(df)
            elif viz_type == "pie_chart":
                data = _prepare_pie_chart(df)
            elif viz_type == "heatmap":
                data = _prepare_heatmap(df)
            else:
                continue
                
            if data:  # Only add if preparation was successful
                prepared_data[viz_type] = data
                
        except Exception as e:
            print(f"⚠️ Error preparing {viz_type}: {e}")
            continue
    
    state.data["prepared_viz_data"] = prepared_data
    state.data["data_preparation_success"] = len(prepared_data) > 0
    
    return state


# Data preparation functions for specific visualization types
def _prepare_bar_graph(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for bar graph visualization."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    num_cols = df.select_dtypes(include=["number"]).columns
    
    if len(cat_cols) == 0 or len(num_cols) == 0:
        return None
        
    cat, num = cat_cols[0], num_cols[0]
    grouped = df.groupby(cat)[num].sum().reset_index()
    
    return {"df": grouped, "x": cat, "y": num}


def _prepare_line_graph(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for line graph visualization."""
    # Look for date columns
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    num_cols = df.select_dtypes(include=["number"]).columns
    
    if len(num_cols) == 0:
        return None
        
    # Use date column if available, otherwise first object column
    if date_cols:
        time_col = date_cols[0]
    else:
        obj_cols = df.select_dtypes(include=["object"]).columns
        if len(obj_cols) == 0:
            return None
        time_col = obj_cols[0]
    
    sorted_df = df.sort_values(time_col)
    return {"df": sorted_df, "time_col": time_col, "value_col": num_cols[0]}


def _prepare_histogram(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for histogram visualization."""
    num_cols = df.select_dtypes(include=["number"]).columns
    
    if len(num_cols) == 0:
        return None
        
    return {"df": df, "var": num_cols[0]}


def _prepare_box_plot(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for box plot visualization."""
    num_cols = df.select_dtypes(include=["number"]).columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    
    if len(num_cols) == 0:
        return None
        
    cat = cat_cols[0] if len(cat_cols) > 0 else None
    return {"df": df, "var": num_cols[0], "cat": cat}


def _prepare_scatter(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for scatter plot visualization."""
    num_cols = df.select_dtypes(include=["number"]).columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    
    if len(num_cols) < 2:
        return None
        
    category = cat_cols[0] if len(cat_cols) > 0 else None
    return {"df": df, "x": num_cols[0], "y": num_cols[1], "category": category}


def _prepare_pie_chart(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for pie chart visualization."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    
    if len(cat_cols) == 0:
        return None
        
    return {"df": df, "cat": cat_cols[0]}


def _prepare_heatmap(df: pd.DataFrame) -> Dict[str, Any]:
    """Prepare data for heatmap visualization."""
    num_df = df.select_dtypes(include=["number"])
    
    if len(num_df.columns) < 2:
        return None
        
    return {"df": num_df.corr()}