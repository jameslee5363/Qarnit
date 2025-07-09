import sys
import os
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.retriever_preprocessor_graph import build_data_pipeline
from agents.state import AppState

pipeline = build_data_pipeline()

# Create initial state
initial_state = AppState()
initial_state.set_initial_question("What's the total USD amount for each purchase order? Show me the top 5 and prepare it for analysis")

result = pipeline.invoke(initial_state)

print("Pipeline result:", result) 
