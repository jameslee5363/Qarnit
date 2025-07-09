"""
Visualization Type Classifier for Visualizer Agent
Uses LLM to classify appropriate visualization types based on DataFrame characteristics.
"""

from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import llm
from agents.state import AppState


def classify_visualization_type(state: AppState) -> AppState:
    """
    Use LLM to classify appropriate visualization types for the DataFrame.
    Expects viz_context to be set by data_inspector.
    """
    viz_context = state.data.get("viz_context")
    if not viz_context:
        state.set_error("No visualization context found. Run data_inspector first.")
        return state
    
    description = viz_context["description"]
    
    # Build LLM prompt for classification (OPTIMIZED VERSION - technical_precise_v2)
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a statistical visualization expert with deep knowledge of data science principles. "
                "Select the most statistically appropriate and insightful visualizations.\n\n"
                "VISUALIZATION RULES:\n"
                "• line_graph: Time series data, sequential patterns, trends over time\n"
                "• bar_graph: Categorical comparisons with numerical values, group comparisons\n"
                "• pie_chart: Part-to-whole relationships (only if ≤6 categories and meaningful proportions)\n"
                "• histogram: Distribution analysis of single numerical variable, frequency analysis\n"
                "• box_plot: Distribution comparison across categories, outlier detection, quartile analysis\n"
                "• scatter: Correlation/relationship between 2 numerical variables, trend identification\n"
                "• heatmap: Correlation matrix for 3+ numerical variables, pattern detection\n\n"
                "ANALYSIS PRIORITY:\n"
                "1. Identify temporal patterns (dates/timestamps) → line_graph\n"
                "2. Assess correlation opportunities (multiple numerical) → scatter/heatmap\n"
                "3. Evaluate categorical-numerical relationships → bar_graph/box_plot\n"
                "4. Consider distribution analysis needs → histogram/box_plot\n\n"
                "Output exactly 2-3 recommendations in this format:\n"
                "1. visualization_type\n"
                "2. visualization_type\n"
                "3. visualization_type"
            )
        ),
        (
            "human",
            "Analyze this DataFrame for optimal visualization selection:\n{description}\n\nRecommend the most appropriate visualizations:"
        )
    ])
    
    try:
        response = llm.invoke(prompt_template.format_messages(description=description))
        raw_response = response.content.strip()
        
        # Parse response to extract visualization types
        viz_types = []
        for line in raw_response.split('\n'):
            line = line.strip()
            if line and ('.' in line or line in ['line_graph', 'bar_graph', 'pie_chart', 'histogram', 'box_plot', 'scatter', 'heatmap']):
                # Extract type after number if present
                if '.' in line:
                    viz_type = line.split('.', 1)[-1].strip()
                else:
                    viz_type = line.strip()
                
                # Clean up common variations
                viz_type = viz_type.replace('_', '_').lower()
                if viz_type in ['line_graph', 'bar_graph', 'pie_chart', 'histogram', 'box_plot', 'scatter', 'heatmap']:
                    viz_types.append(viz_type)
        
        # Store results in viz_context
        if "viz_context" not in state.data:
            state.data["viz_context"] = {}
        
        state.data["viz_context"]["recommended_viz_types"] = viz_types
        state.data["viz_context"]["raw_classification_response"] = raw_response
        state.data["viz_classification_success"] = True
        
    except Exception as e:
        state.set_error(f"Visualization classification failed: {str(e)}")
        state.data["viz_classification_success"] = False
    
    return state


def parse_viz_types(viz_types_string: str) -> list:
    """
    Parse the LLM response into a clean list of visualization types.
    Utility function for extracting visualization types from LLM output.
    """
    types = []
    for line in viz_types_string.split('\n'):
        line = line.strip()
        if line and ('.' in line):
            # Extract type after the number (e.g., "1. bar_graph" -> "bar_graph")
            viz_type = line.split('.', 1)[-1].strip()
            if viz_type in ['line_graph', 'bar_graph', 'pie_chart', 'histogram', 'box_plot', 'scatter', 'heatmap']:
                types.append(viz_type)
    return types
