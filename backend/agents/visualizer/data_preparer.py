import pandas as pd
from typing import Dict, Any

# Prepare data for visualization based on the type requested
# Returns a transformed DataFrame and a configuration dictionary for the chart.

def prepare_data(df: pd.DataFrame, vis_type: str) ->  Dict[str, Any]:
    # If multiple types returned, pick the first
    # ==TASK: If there are multiple types, we should handle them all
    types = [t.strip()[3:] for t in vis_type.split('\n')]
    print(types)
    dic=dict()
    #tech = types[0] 
    for tech in types :
        try:
    # == TASK: Need to test every visualization type - please be aware that not every method is complete
    # == TASK: Need to handle cases where no data is available for a specific visualization type
        # 1) Bar graph (vertical bar): compare sums across categories
            if tech == "bar_graph":
                cat_cols = df.select_dtypes(include=["object", "category"]).columns
                num_cols = df.select_dtypes(include=["int64", "float64"]).columns  
                if len(cat_cols) == 0:
                    raise ValueError("No categorical columns found in the DataFrame for bar graph.")
                elif len(num_cols) == 0:
                    raise ValueError("No numerical columns (int64 or float64) found in the DataFrame for bar graph.")
                # if len(cat_cols) == 0 or len(num_cols) == 0:
                   # raise ValueError("Bar graph requires at least one categorical and one numerical column.")
                cat = cat_cols[0]
                num = num_cols[0]
                grouped = df.groupby(cat)[num].sum().reset_index()
                dic["bar_graph"] = {"df": grouped, "x": cat, "y": num}

        # 2) Line graph: time series
            elif tech == "line_graph":
                date_cols = [c for c in df.columns if "date" in c.lower()]
                num  = df.select_dtypes(include=["number"]).columns[0]
                date = date_cols[0] if date_cols else df.select_dtypes(include=["object"]).columns[0]
                sorted_df = df.sort_values(date)
                dic["line_graph"]={"time_col": date, "value_col": num, "df": sorted_df}

        # 3) Histogram: distribution of a numeric variable
            elif tech == "histogram":
                var = df.select_dtypes(include=["number"]).columns[0]
                dic["histogram"]={"var": var, "df": df}

        # 4) Box plot: distribution and outliers per category or overall
            elif tech == "box_plot":
                num_cols = df.select_dtypes(include=["number"]).columns
                cat_cols = df.select_dtypes(include=["object","category"]).columns
                if len(cat_cols)>0:
                    dic["box_plot"]={"cat": cat_cols[0], "var": num_cols[1], "df": df}
                else:
                    dic["box_plot"]={"cat": None, "var": num_cols[1], "df": df}

        # 5) Scatter: relationship between two numeric variables
            elif tech == "scatter":
                nums = df.select_dtypes(include=["number"]).columns
                cats = df.select_dtypes(include=["object"]).columns
                if len(nums) >= 2:
                    cat = cats[0] if cats.any() else None
                    dic["scatter"]={"x": nums[0], "y": nums[1], "category": cat, "df": df}
                else:
                    raise ValueError("Scatter plot requires at least two numerical columns.")
                    #return df, {}

        # 6) Pie chart: proportions of categories
            elif tech == "pie_chart":
                cat = df.select_dtypes(include=["object","category"]).columns[1]
                dic["pie_chart"]={"cat": cat, "df": df}

        # 7) Heatmap: correlation matrix
            elif tech == "heatmap":
                num_df = df.select_dtypes(include=["number"])
                dic["heatmap"]={"df": num_df.corr()}
                
        except Exception as e : 
            print (f"⚠️ An error occurred with {tech}: {e}")
            continue

    # No applicable visualization type
    #raise ValueError("❌ No valid visualization can be generated with the given types and available data.")

    #Fallback: return raw
    #dic["df"]=df
    return dic