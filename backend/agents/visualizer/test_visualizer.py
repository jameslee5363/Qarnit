import pandas as pd
from typing import Any, Optional
from df_inspector import inspect_df
from feasibility_checker import check_feasibility
from vis_type_classifier import classify_vis_type
from data_preparer import prepare_data
from plot_data import plot_data
from data_description import describe_dataframe_for_llm

def run_visualizer(df: pd.DataFrame) -> Optional[Any]:
    # 1) Inspect
    ctx = inspect_df(df)

    # 2) Feasibility
    if not check_feasibility(df):
        print("⚠️ DataFrame too small or no plottable columns.")
        return None
    
    # 3) Data description
    des=describe_dataframe_for_llm(df)
    
    # 3) Classify
    vis_type = classify_vis_type(df,des)

    # 4) Prepare
    dic = prepare_data(df, vis_type)
    print(dic)
    # 5) Plot
   
    print(vis_type)
    plot = plot_data(dic)

    return plot

# Example usage
if __name__ == "__main__":
    data_bar = pd.read_csv("./Datasets/aa.csv")
    df_mock = pd.DataFrame(data_bar)
    des=describe_dataframe_for_llm(df_mock)

    test = classify_vis_type(df_mock,des)

    print(test)
    plots=run_visualizer(df_mock)
    for plot in plots :
        plot.show()
        print(plot)
