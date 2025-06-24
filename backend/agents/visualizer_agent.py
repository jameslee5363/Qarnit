from agent import Agent
from state import AgentState
from database_manager import DatabaseManager
from llm_manager import LLMManager
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
import viz_utils

class VisualizerAgent(Agent):
    def __init__(self):
        super().__init__()
        self.db_manager  = DatabaseManager()
        self.llm_manager = LLMManager()

    def run(self, state: AgentState) -> AgentState:

        return 0
    

    ##== Helper methods
    def _is_feasible(self, df: pd.DataFrame) -> bool:
        # Need at least 2 rows and ≥1 numeric or categorical column
        if df is None or df.shape[0] < 2:
            return False
        usable = df.select_dtypes(include=["number", "object", "category"])
        return not usable.empty
    
    def _classify_vis_type(self, df: pd.DataFrame) -> str:
        """
        Uses LLM to select the best visualization category for the DataFrame.
        
        """
        # Prepare schema summary
        dtypes = df.dtypes.astype(str).to_dict()
        sample = df.head(5).to_dict(orient='records')
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
             You are an AI assistant that recommends one or more appropriate visualization techniques for a given Pandas DataFrame.  
             Below are the available techniques and when to use each:
                - bar_graph: Compare values across discrete categories; bars extend horizontally.
                - line_graph: Show trends or ordered series (e.g., time series data).
                - histogram: Display the frequency distribution of a single numeric variable.
                - box_plot: Illustrate the distribution, central tendency, and outliers of a numeric variable (optionally grouped by category).
                - scatter: Show the relationship between two numeric variables. (emphasizes point-wise relationships in two dimensions)
                - pie_chart: Visualize proportions of a whole for a single categorical variable.
                - heatmap: Display values across two categorical axes or show a correlation matrix of multiple variables.
             
             When you respond, choose **one or more** techniques from the list above.
             Output them as a comma-separated list, with no extra text or space.
             """), 
            ("human", """
             ===DataFrame columns and types: 
             {dtypes}

             ===Sample rows (up to 5): 
             {sample}
             
             Which visualization techniques from the list above best fit this DataFrame?"""),
        ])

        resp = self.llm_manager.invoke(prompt, dtypes=dtypes, sample=sample)
        return resp.strip().lower()
    
    def _prepare_data(self, df: pd.DataFrame, vis_type: str) -> tuple[pd.DataFrame, dict]:
        """
        Prepare the DataFrame and keyword args for the chosen visualization type.
        """
        # If multiple types returned, pick the first
        types = [t.strip() for t in vis_type.split(',')]
        tech = types[0]

        # 1) Bar graph (vertical bar): compare sums across categories
        if tech == "bar_graph":
            cat = df.select_dtypes(include=["object","category"]).columns[0]
            num = df.select_dtypes(include=["number"]).columns[0]
            grouped = df.groupby(cat)[num].sum().reset_index()
            return grouped, {"x": cat, "y": num}

        # 2) Line graph: time series
        if tech == "line_graph":
            date_cols = [c for c in df.columns if "date" in c.lower()]
            date = date_cols[0] if date_cols else df.select_dtypes(include=["object"]).columns[0]
            num  = df.select_dtypes(include=["number"]).columns[0]
            sorted_df = df.sort_values(date)
            return sorted_df, {"time_col": date, "value_col": num}

        # 3) Histogram: distribution of a numeric variable
        if tech == "histogram":
            var = df.select_dtypes(include=["number"]).columns[0]
            return df, {"var": var}

        # 4) Box plot: distribution and outliers per category or overall
        if tech == "box_plot":
            num_cols = df.select_dtypes(include=["number"]).columns
            cat_cols = df.select_dtypes(include=["object","category"]).columns
            if cat_cols.any():
                return df, {"cat": cat_cols[0], "var": num_cols[0]}
            else:
                return df, {"cat": None, "var": num_cols[0]}

        # 5) Scatter: relationship between two numeric variables
        if tech == "scatter":
            nums = df.select_dtypes(include=["number"]).columns
            cats = df.select_dtypes(include=["object"]).columns
            if len(nums) >= 2:
                cat = cats[0] if cats.any() else None
                return df, {"x": nums[0], "y": nums[1], "category": cat}
            else:
                return df, {}

        # 6) Pie chart: proportions of categories
        if tech == "pie_chart":
            cat = df.select_dtypes(include=["object","category"]).columns[0]
            return df, {"cat": cat}

        # 7) Heatmap: correlation matrix
        if tech == "heatmap":
            num_df = df.select_dtypes(include=["number"])
            return num_df, {}

        # Fallback: return raw
        return df, {}
    
    def _plot_data(self, df: pd.DataFrame, viz_type: str, **kwargs):
        # pick first technique
        # Handle the case when there are more than one suggested viz type
        if viz_type == "bar_graph":
            # kwargs: x, y
            return viz_utils.plot_bar(df, kwargs["x"], kwargs["y"])
        
        elif viz_type == "line_graph":
            # kwargs: time_col, value_col
            return viz_utils.plot_line(df, kwargs["time_col"], kwargs["value_col"])
        
        elif viz_type == "histogram":
            # kwargs: var
            return viz_utils.plot_histogram(df, kwargs["var"])
        
        elif viz_type == "box_plot":
            # kwargs: var, cat (cat may be None)
            return viz_utils.plot_box(df, kwargs.get("var"), kwargs.get("cat"))
        
        elif viz_type == "scatter":
            # kwargs: x, y, category (optional)
            return viz_utils.plot_scatter(
                df,
                kwargs.get("x"),
                kwargs.get("y"),
                category=kwargs.get("category")
            )

        elif viz_type == "pie_chart":
            # kwargs: cat
            return viz_utils.plot_pie(df, kwargs["cat"])

        elif viz_type == "heatmap":
            # no kwargs
            return viz_utils.plot_heatmap(df)

        # unknown
        return None



        
    




