import sys
import os
import json
import pandas as pd
import re
import ast
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graphs.retrieval_graph import build_retriever_graph

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def extract_column_names_from_query(query: str):
    """Extract column names from SQL SELECT statement"""
    try:
        # Remove comments and normalize whitespace
        query = re.sub(r'--.*', '', query, flags=re.MULTILINE)
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Find the SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return None
        
        select_clause = select_match.group(1)
        
        # Split by comma and clean up each column
        columns = []
        for col in select_clause.split(','):
            col = col.strip()
            
            # Handle AS aliases
            if ' AS ' in col.upper():
                alias = col.split(' AS ')[-1].strip()
                # Remove quotes if present
                alias = alias.strip('"\'`')
                columns.append(alias)
            else:
                # Extract column name (handle table.column format)
                col_name = col.split('.')[-1] if '.' in col else col
                # Remove quotes and functions
                col_name = re.sub(r'^[A-Z]+\(', '', col_name)  # Remove functions like SUM(
                col_name = re.sub(r'\)$', '', col_name)  # Remove closing parenthesis
                col_name = col_name.strip('"\'`')
                columns.append(col_name)
        
        return columns if columns else None
        
    except Exception as e:
        print(f"⚠️ Could not extract column names from query: {e}")
        return None

def extract_dataframe_from_retrieval(result):
    """Extract DataFrame from retrieval result"""
    if not result.get("messages"):
        return None
    
    # Look for the last ToolMessage with sql_db_query results
    sql_result = None
    query_info = None
    
    for msg in reversed(result["messages"]):
        # Check if this is a ToolMessage from sql_db_query
        if (hasattr(msg, 'name') and msg.name == 'sql_db_query' and 
            hasattr(msg, 'content') and msg.content):
            sql_result = msg.content
            break
        
        # Also look for the AI message with the SQL query to get column names
        if (hasattr(msg, 'tool_calls') and msg.tool_calls and 
            len(msg.tool_calls) > 0 and msg.tool_calls[0].get('name') == 'sql_db_query'):
            query_info = msg.tool_calls[0].get('args', {}).get('query', '')
    
    if not sql_result:
        print("⚠️ No SQL query results found in messages")
        return None
    
    try:
        # Parse the tuple string result: "[(144644, 14034993.0), (146488, 7901314.4), ...]"
        data_tuples = ast.literal_eval(sql_result)
        
        if not data_tuples:
            print("⚠️ Empty query result")
            return None
        
        # Extract column names from the SQL query if available
        column_names = extract_column_names_from_query(query_info) if query_info else None
        
        # If we can't extract column names, create generic ones
        if not column_names:
            num_cols = len(data_tuples[0]) if data_tuples else 0
            column_names = [f"column_{i}" for i in range(num_cols)]
        
        # Create DataFrame
        df = pd.DataFrame(data_tuples, columns=column_names)
        
        print(f"✅ Extracted DataFrame: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"   Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error parsing SQL result: {e}")
        print(f"   Raw content: {sql_result}")
        return None

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
final_result = None
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
    
    # Store the final result
    final_result = step
    
    # Pause for readability (remove this if you want continuous output)
    input("Press Enter to continue to next step...")

print_separator("FINAL SUMMARY")
print(f"Total steps executed: {step_count}")
print("Agent execution completed!")

print_separator("EXTRACTED DATAFRAME")
if final_result:
    print("Attempting to extract DataFrame from final result...")
    df = extract_dataframe_from_retrieval(final_result)
    
    if df is not None:
        print("\n🎉 SUCCESSFULLY EXTRACTED DATAFRAME:")
        print("="*50)
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Columns: {list(df.columns)}")
        print("\nData:")
        print(df.to_string(index=False))
        print("\nDataFrame Info:")
        print(df.info())
        print("\nSummary Statistics:")
        print(df.describe())
    else:
        print("❌ Failed to extract DataFrame from the result")
        print("Final result structure:")
        pprint(final_result)
else:
    print("❌ No final result available")