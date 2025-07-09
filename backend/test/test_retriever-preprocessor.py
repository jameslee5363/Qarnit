import sys
import os
import importlib

retriever_preprocessor_module = importlib.import_module('backend.graphs.retriever-preprocessor_graph')
build_data_pipeline = retriever_preprocessor_module.build_data_pipeline

from backend.agents.state import AppState

pipeline = build_data_pipeline()

# Create initial state
initial_state = AppState()
initial_state.set_initial_question("What's the total USD amount for each purchase order? Show me the top 5 and prepare it for analysis")

result = pipeline.invoke(initial_state)

print("Pipeline result:", result) 
