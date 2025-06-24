import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional

def plot_bar(df: pd.DataFrame, x: str, y: str) -> plt.Figure: # tested
    fig, ax = plt.subplots()
    # Aggregate and sort values
    agg = df.groupby(x)[y].sum().sort_values()
    # Plot horizontal bars
    ax.barh(agg.index.astype(str), agg.values)
    ax.set_ylabel(x)
    ax.set_xlabel(y)
    ax.set_title(f"{y} by {x}")
    fig.autofmt_xdate(rotation=45)
    return fig


def plot_line(df: pd.DataFrame, time_col: str, value_col: str) -> plt.Figure: # tested 
    fig, ax = plt.subplots()
    ts = df.sort_values(time_col)
    ax.plot(ts[time_col], ts[value_col], marker='o')
    ax.set_xlabel(time_col)
    ax.set_ylabel(value_col)
    ax.set_title(f"Trend of {value_col} over {time_col}")
    fig.autofmt_xdate()
    return fig


def plot_histogram(df: pd.DataFrame, var: str, bins): ### ****** need to edit the bin size
    fig, ax = plt.subplots()
    ax.hist(df[var].dropna(), bins=bins)
    ax.set_xlabel(var)
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of {var}")
    return fig


def plot_box(df: pd.DataFrame, var: str, cat: str = None): #  tested
    fig, ax = plt.subplots()
    if cat:
        df.boxplot(column=var, by=cat, ax=ax)
        ax.set_title(f"{var} by {cat}")
        ax.set_xlabel(cat)
    else:
        df.boxplot(column=var, ax=ax)
        ax.set_title(f"Distribution of {var}")
        ax.set_xlabel("")
    ax.set_ylabel(var)
    fig.suptitle("")  # remove automatic title
    return fig


def plot_pie(df: pd.DataFrame, cat:str) -> plt.Figure:
    fig, ax = plt.subplots()
    counts = df[cat].value_counts()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
    ax.set_title(f"Proportion of {cat}")
    return fig


def plot_scatter(df: pd.DataFrame, x: str, y: str, category: Optional[str] = None) -> plt.Figure: #tested
    """
    Scatter plot of x vs y, optionally color-coded by category.
    """
    fig, ax = plt.subplots()
    if category and category in df.columns:
        for name, grp in df.groupby(category):
            ax.scatter(grp[x], grp[y], label=str(name))
        ax.legend()
    else:
        ax.scatter(df[x], df[y])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {x}")
    return fig


def plot_heatmap():

    return 0