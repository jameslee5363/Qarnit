import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graphs.retrieval_graph import build_retriever_agent_graph

agent = build_retriever_agent_graph()
question = "What's the total USD amount for each purchase order? Show me the top 5"

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()