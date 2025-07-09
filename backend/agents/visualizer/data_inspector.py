"""
DataFrame Inspector for Visualizer Agent
Generates detailed descriptions of DataFrames for downstream processing.
"""

import pandas as pd
from typing import Dict, Any
from agents.state import AppState


def inspect_dataframe(state: AppState) -> AppState:
    """
    Inspect DataFrame and generate comprehensive description.
    Similar to preprocessor's df_inspector but focused on visualization needs.
    """
    df = state.data.get("df")
    if df is None:
        state.set_error("No DataFrame found in state")
        return state
    
    # Generate detailed description
    description = _describe_dataframe_for_llm(df)
    
    # Store in state
    state.data["viz_context"] = {
        "description": description,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "shape": df.shape,
        "sample": df.head(3).to_dict(orient="records")
    }
    
    return state


def _describe_dataframe_for_llm(df: pd.DataFrame) -> str:
    """Generate detailed textual description of DataFrame for LLM."""
    n_rows, n_cols = df.shape
    description = [f"The dataset contains {n_rows} rows and {n_cols} columns.\n"]

    # Column types summary
    type_counts = df.dtypes.value_counts()
    for dtype, count in type_counts.items():
        description.append(f"- {count} columns of type {dtype}.")
    description.append("")

    # Numerical columns analysis
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols):
        description.append("### Numerical columns:")
        for col in num_cols:
            desc = df[col].describe()
            description.append(
                f"- **{col}**: mean = {desc['mean']:.2f}, min = {desc['min']}, max = {desc['max']}, std = {desc['std']:.2f}."
            )
    else:
        description.append("No numerical columns detected.")

    description.append("")

    # Categorical columns analysis
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols):
        description.append("### Categorical columns:")
        for col in cat_cols:
            top = df[col].value_counts().head(3)
            description.append(f"- **{col}**: {len(df[col].unique())} unique values. Top values: " + 
                               ", ".join([f"{val} ({cnt})" for val, cnt in top.items()]))
    else:
        description.append("No categorical columns detected.")

    description.append("")

    # Missing values analysis
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if not missing_cols.empty:
        description.append("### Missing values:")
        for col, count in missing_cols.items():
            description.append(f"- **{col}**: {count} missing values ({count/n_rows:.1%})")
    else:
        description.append("No missing values detected.")

    return "\n".join(description)
