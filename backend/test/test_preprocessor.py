import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.preprocessor.suggest_preprocessing import suggest_preprocessing
from agents.preprocessor.df_inspector import inspect_df
import pandas as pd
from agents.preprocessor.relevance_checker import check_relevance
from agents.preprocessor.code_generator import generate_code
from agents.preprocessor.code_executor import execute_code

df = pd.read_csv("data/dummy_po.csv")

user_instruction = "Verify that PO Number is unique; if there are duplicates, decide to merge or remove redundant rows."

print(inspect_df(df))