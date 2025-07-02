import sys
import os
import pandas as pd
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graphs.preprocessor_graph import build_preprocessor_graph

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def inspect_state_structure(state, step_num):
    print(f"\nSTEP {step_num} - State Structure:")
    print(f"State keys: {list(state.keys())}")
    print(f"State type: {type(state)}")
    
    # Show all non-messages keys and their values
    for key, value in state.items():
        if key != "messages":
            print(f"  {key}: {type(value)} = {repr(value)}")
    
    # Show messages structure
    if "messages" in state:
        print(f"  messages: {len(state['messages'])} messages")
        for i, msg in enumerate(state["messages"]):
            print(f"    Message {i}: {type(msg).__name__}")
            if hasattr(msg, 'content'):
                content_preview = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                print(f"      Content: {content_preview}")

agent = build_preprocessor_graph()

# Load the data
df = pd.read_csv("./backend/data/dummy_po.csv")
user_instruction = "Verify that PO Number is unique; if there are duplicates, decide to merge or remove redundant rows."

print_separator("INITIAL SETUP")
print(f"DataFrame shape: {df.shape}")
print(f"DataFrame columns: {list(df.columns)}")
print(f"User instruction: {user_instruction}")

# Initial state - Note: This agent seems to work with dataframes, not just messages
print_separator("INITIAL INPUT STATE")
initial_state = {
    "messages": [{"role": "user", "content": user_instruction}],
    "df": df  # Adding DataFrame to state
}
print("Initial state structure:")
for key, value in initial_state.items():
    if key == "df":
        print(f"  {key}: pandas.DataFrame {value.shape}")
    else:
        print(f"  {key}: {type(value)} = {repr(value)}")

print_separator("STREAMING THROUGH PREPROCESSOR STEPS")

step_count = 0
for step in agent.stream(
    initial_state,
    stream_mode="values",
):
    step_count += 1
    print_separator(f"STEP {step_count}")
    
    inspect_state_structure(step, step_count)
    
    # Show any new keys that appeared
    if step_count == 1:
        initial_keys = set(initial_state.keys())
    
    current_keys = set(step.keys())
    new_keys = current_keys - initial_keys if step_count > 1 else set()
    
    if new_keys:
        print(f"\nNew keys added: {new_keys}")
        for key in new_keys:
            print(f"  {key}: {type(step[key])} = {repr(step[key])}")
    
    # Check for any parsed data structures
    for key in step.keys():
        if "parsed" in key.lower():
            print(f"\nParsed data structure - {key}:")
            pprint(step[key])
    
    print(f"\nFull state keys evolution: {list(step.keys())}")
    
    # Pause for examination
    input("Press Enter to continue to next step...")

print_separator("FINAL SUMMARY")
print(f"Total steps executed: {step_count}")
print("Preprocessor agent execution completed!")

# Show final state summary
if step_count > 0:
    print("\nFinal state summary:")
    final_step = step  # Last step from the loop
    for key, value in final_step.items():
        if key == "df":
            print(f"  {key}: DataFrame shape {value.shape}")
        elif key == "messages":
            print(f"  {key}: {len(value)} messages")
        else:
            print(f"  {key}: {type(value)}")