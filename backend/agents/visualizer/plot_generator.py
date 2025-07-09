"""
Plot Generator for Visualizer Agent
Creates matplotlib plots from prepared visualization data.
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any, Optional
from agents.state import AppState


def generate_plots(state: AppState) -> AppState:
    """
    Generate matplotlib plots from prepared visualization data.
    Expects prepared_viz_data to be set by data_preparer.
    """
    prepared_data = state.data.get("prepared_viz_data")
    
    if not prepared_data:
        state.set_error("No prepared visualization data found. Run data_preparer first.")
        return state
    
    generated_plots = []
    
    for plot_type, params in prepared_data.items():
        try:
            if plot_type == "bar_graph":
                fig = _create_bar_plot(**params)
            elif plot_type == "line_graph":
                fig = _create_line_plot(**params)
            elif plot_type == "histogram":
                fig = _create_histogram(**params)
            elif plot_type == "box_plot":
                fig = _create_box_plot(**params)
            elif plot_type == "scatter":
                fig = _create_scatter_plot(**params)
            elif plot_type == "pie_chart":
                fig = _create_pie_chart(**params)
            elif plot_type == "heatmap":
                fig = _create_heatmap(**params)
            else:
                continue
                
            generated_plots.append({
                "type": plot_type,
                "figure": fig
            })
            
        except Exception as e:
            print(f"⚠️ Error generating {plot_type}: {e}")
            continue
    
    state.data["generated_plots"] = generated_plots
    state.data["plot_generation_success"] = len(generated_plots) > 0
    
    return state


# Individual plot creation functions
def _create_bar_plot(df: pd.DataFrame, x: str, y: str) -> plt.Figure:
    """Create horizontal bar plot."""
    fig, ax = plt.subplots(figsize=(10, 6))
    agg = df.groupby(x)[y].sum().sort_values()
    ax.barh(agg.index.astype(str), agg.values)
    ax.set_ylabel(x)
    ax.set_xlabel(y)
    ax.set_title(f"{y} by {x}")
    plt.tight_layout()
    return fig


def _create_line_plot(df: pd.DataFrame, time_col: str, value_col: str) -> plt.Figure:
    """Create line plot for time series data."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ts = df.sort_values(time_col)
    ax.plot(ts[time_col], ts[value_col], marker='o', linewidth=2)
    ax.set_xlabel(time_col)
    ax.set_ylabel(value_col)
    ax.set_title(f"Trend of {value_col} over {time_col}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def _create_histogram(df: pd.DataFrame, var: str, bins: int = 20) -> plt.Figure:
    """Create histogram for distribution analysis."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df[var].dropna(), bins=bins, alpha=0.7, edgecolor='black')
    ax.set_xlabel(var)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of {var}")
    plt.tight_layout()
    return fig


def _create_box_plot(df: pd.DataFrame, var: str, cat: Optional[str] = None) -> plt.Figure:
    """Create box plot for distribution and outlier analysis."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if cat and cat in df.columns:
        df.boxplot(column=var, by=cat, ax=ax)
        ax.set_title(f"{var} Distribution by {cat}")
        ax.set_xlabel(cat)
    else:
        df.boxplot(column=var, ax=ax)
        ax.set_title(f"Distribution of {var}")
        ax.set_xlabel("")
    
    ax.set_ylabel(var)
    fig.suptitle("")  # Remove automatic title
    plt.tight_layout()
    return fig


def _create_pie_chart(df: pd.DataFrame, cat: str) -> plt.Figure:
    """Create pie chart for categorical proportions."""
    fig, ax = plt.subplots(figsize=(8, 8))
    counts = df[cat].value_counts()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(f"Proportion of {cat}")
    return fig


def _create_scatter_plot(df: pd.DataFrame, x: str, y: str, category: Optional[str] = None) -> plt.Figure:
    """Create scatter plot for relationship analysis."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if category and category in df.columns:
        for name, group in df.groupby(category):
            ax.scatter(group[x], group[y], label=str(name), alpha=0.7)
        ax.legend()
    else:
        ax.scatter(df[x], df[y], alpha=0.7)
    
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {x}")
    plt.tight_layout()
    return fig


def _create_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Create correlation heatmap."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Use seaborn style if available, otherwise matplotlib
    try:
        import seaborn as sns
        sns.heatmap(df, annot=True, cmap="coolwarm", center=0, ax=ax)
    except ImportError:
        cax = ax.matshow(df, cmap="coolwarm")
        fig.colorbar(cax)
        ax.set_xticks(range(len(df.columns)))
        ax.set_yticks(range(len(df.index)))
        ax.set_xticklabels(df.columns, rotation=90)
        ax.set_yticklabels(df.index)
    
    ax.set_title("Correlation Heatmap", pad=20)
    plt.tight_layout()
    return fig


# Utility functions
def save_plots(plots: List[Dict[str, Any]], output_dir: str = "./plots/") -> List[str]:
    """
    Save generated plots to files.
    Returns list of saved file paths.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    for i, plot_data in enumerate(plots):
        plot_type = plot_data["type"]
        figure = plot_data["figure"]
        
        filename = f"{plot_type}_{i+1}.png"
        filepath = os.path.join(output_dir, filename)
        
        figure.savefig(filepath, dpi=300, bbox_inches='tight')
        saved_files.append(filepath)
        
    return saved_files


def display_plots(plots: List[Dict[str, Any]]) -> None:
    """Display all generated plots."""
    for plot_data in plots:
        plt.figure(plot_data["figure"].number)
        plt.show()
