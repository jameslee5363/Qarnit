import pandas as pd
from viz_utils import Visualizer
from typing import Any, Dict


def plot_data(dic : dict) -> Any:
    # Handle the case when there are more than one suggested viz type
    #viz_type=[t.strip()[3:] for t in viz_type.split('\n')]
    res=[]
    vis= Visualizer()
    # Check if the requested type exists in the dictionary
    for type,v in dic.items():
            #if type not in dic :
            # raise ValueError(f"Visualization type {type} is not found in the prepared data")
        params = dic[type]
            #if type == "bar_graph":
                    # kwargs: x, y
        res.append(vis.vis_funcs[type](**params))
        print("done")
        """ elif type == "line_graph":
            # kwargs: time_col, value_col
            res.append(viz_utils.plot_line(df, params["time_col"], params["value_col"]))
        
        elif type == "histogram":
            # kwargs: var 
            res.append(viz_utils.plot_histogram(df, params["var"]))
        
        elif type == "box_plot":
            # kwargs: var , cat (categorical or None)
            cat = params.get("cat", None)
            res.append(viz_utils.plot_box(df, params["var"], cat))
        
        elif type == "scatter":
            # kwargs: x, y, category (optional)
            category = params.get("category", None)
            res.append(viz_utils.plot_scatter(df, params["x"], params["y"], category))

        elif type == "pie_chart":
            # kwargs: cat 
            res.append(viz_utils.plot_pie(df, params["cat"]))

        elif type == "heatmap":
            # kwargs: heatmap True 
            # df is corr matrix
            res.append(viz_utils.plot_heatmap(df))
        else:
            raise ValueError(f"Visualization type '{type}' is not supported.")"""
    return res

    # == TASK: Need to test every visualization type - please be aware that not every method is complete
