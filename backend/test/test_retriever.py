import sys
import os
import json
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graphs.retrieval_graph import build_retriever_graph

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def inspect_message(msg, index):
    print(f"\nMessage {index}:")
    print(f"  Type: {type(msg)}")
    print(f"  Role: {getattr(msg, 'role', 'N/A')}")
    print(f"  Tool calls: {getattr(msg, 'tool_calls', 'N/A')}")
    print(f"  Tool call ID: {getattr(msg, 'tool_call_id', 'N/A')}")
agent = build_retriever_graph()
question = "What's the total USD amount for each purchase order? Show me the top 5"

print_separator("INITIAL INPUT")
initial_state = {"messages": [{"role": "user", "content": question}]}
print("Initial state structure:")
pprint(initial_state)

print_separator("STREAMING THROUGH AGENT STEPS")

step_count = 0
for step in agent.stream(
    initial_state,
    stream_mode="values",
):
    step_count += 1
    print_separator(f"STEP {step_count}")
    
    print("Full step keys:", list(step.keys()))
    print("Number of messages:", len(step["messages"]))
    
    # Show each message in detail
    for i, msg in enumerate(step["messages"]):
        inspect_message(msg, i)
    
    print(f"\nLast message details:")
    last_msg = step["messages"][-1]
    print(f"  Raw object: {repr(last_msg)}")
    
    # Try to serialize to see the full structure
    try:
        if hasattr(last_msg, 'dict'):
            print(f"  As dict: {last_msg.dict()}")
        elif hasattr(last_msg, '__dict__'):
            print(f"  __dict__: {last_msg.__dict__}")
    except Exception as e:
        print(f"  Serialization error: {e}")
    
    print(f"\nRaw step type: {type(step)}")
    
    # Pause for readability (remove this if you want continuous output)
    input("Press Enter to continue to next step...")

print_separator("FINAL SUMMARY")
print(f"Total steps executed: {step_count}")
print("Agent execution completed!")