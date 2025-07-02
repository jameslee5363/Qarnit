import pandas as pd
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from llm_config import LLMManager
from langchain_core.messages import BaseMessage
from data_description import describe_dataframe_for_llm

def classify_vis_type(df: pd.DataFrame, des : str) -> str:
    """
    Use LLM to pick one or more visualization techniques for the given DataFrame.
    Gathers context via inspect_df.
    Returns a comma-separated list of techniques.+
    """
    # Inspect the DataFrame for context
    dtypes = df.dtypes.astype(str).to_dict()
    sample = df.head(5).to_dict(orient='records')

    llm = LLMManager()

    # Build the prompt using the inspected context
    # == TASK: Use a more sophisticated LLM prompt to classify the visualization type
    prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an AI assistant that recommends one or more appropriate data visualization techniques "
            "for a given Pandas DataFrame. Your recommendations should be based on the DataFrame’s structure, semantics, and sample values. "
            "Choose from the following visualization types: line_graph, bar_graph, pie_chart, histogram, box_plot, scatter, heatmap. "
            "Output your recommendations as a numbered list starting at 1, exactly matching the visualization type names provided. For example:\n"
            "i. visualization_type\n"
            "i+1. visualization_type\n"
            "and so forth.\n"
            "Consider the following when recommending:\n"
            "- For numeric columns, analyze their distributions and correlations.\n"
            "- For categorical columns, analyze frequencies and groupings.\n"
            "- If time series data is detected, prioritize line_graph.\n"
            "Provide only the list of visualization techniques without any additional explanations."
        )
    ),
    (
        "human",
        (
            "Here is a detailed description of the DataFrame:\n"
            "{des}\n\n"
            "Based on this information, which visualization techniques from the list above best fit this DataFrame? "
            "Rank your top recommendations in order."
        )
    )
])


    resp = llm.invoke(prompt_template, des=des)
    return resp.strip().lower()
