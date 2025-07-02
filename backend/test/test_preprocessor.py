import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.preprocessor.suggest_preprocessing import suggest_preprocessing
from agents.preprocessor.df_inspector import inspect_df
import pandas as pd
from agents.preprocessor.relevance_checker import check_relevance
from agents.preprocessor.code_generator import generate_code
from agents.preprocessor.code_executor import execute_code

from graphs.preprocessor_graph import build_preprocessor_graph

agent = build_preprocessor_graph()
print(agent.stream)
"""df = pd.read_csv("./data/dummy_po.csv")
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
user_instruction = "Verify that PO Number is unique; if there are duplicates, decide to merge or remove redundant rows."

print(inspect_df(df))"""