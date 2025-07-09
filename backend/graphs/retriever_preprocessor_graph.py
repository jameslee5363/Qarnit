import os
import sys
import json
from pprint import pprint
from langgraph.graph import StateGraph, START, END, MessagesState
from typing import Literal, Optional, Any
import pandas as pd
import re
import ast
from agents.state import AppState
from graphs.retrieval_graph import build_retriever_graph
from graphs.preprocessor_graph import build_preprocessor_graph

def extract_column_names_from_query(query: str) -> Optional[list]:
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

def extract_dataframe_from_retrieval(result: dict) -> Optional[pd.DataFrame]:
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

def run_retrieval_stage(state: AppState) -> AppState:
    """Execute retrieval agent and extract data"""
    print("🔍 Running retrieval stage...")
    
    try:
        # Build and run retrieval graph
        retrieval_graph = build_retriever_graph()
        result = retrieval_graph.invoke(state)
        
        # Extract DataFrame from retrieval result
        extracted_data = extract_dataframe_from_retrieval(result)
        
        # Update the state with retrieved data
        if extracted_data is not None:
            state.set_retrieved_df(extracted_data)
        
        return state
        
    except Exception as e:
        state.record_extra("error", f"Retrieval failed: {str(e)}")
        return state

def should_preprocess(state: AppState) -> Literal["preprocess", "complete"]:
    """Decide if preprocessing is needed"""
    if state.retrieved_df is not None and not state.extras.get("error"):
        return "preprocess"
    return "complete"

def run_preprocessing_stage(state: AppState) -> AppState:
    """Execute preprocessing agent"""
    print("🛠️ Running preprocessing stage...")
    
    try:
        # Set the preprocessing instruction from the initial question
        # Extract the preprocessing part from the question
        question = state.initial_question
        if "prepare it for analysis" in question.lower():
            preprocessing_instruction = "Prepare this data for analysis by cleaning, normalizing, and creating useful features"
        else:
            preprocessing_instruction = "Clean and prepare this data for analysis"
        
        state.set_preprocessing_instruction(preprocessing_instruction)
        
        # Build preprocessing graph
        preprocessing_graph = build_preprocessor_graph()
        
        # Run preprocessing with the current state
        result = preprocessing_graph.invoke(state)
        
        return result
        
    except Exception as e:
        state.record_extra("error", f"Preprocessing failed: {str(e)}")
        return state

def finalize_pipeline(state: AppState) -> AppState:
    """Final step - add completion message"""
    print("✅ Pipeline complete!")
    
    if state.extras.get("error"):
        final_message = {
            "role": "assistant",
            "content": f"Pipeline completed with error: {state.extras['error']}"
        }
    elif state.retrieved_df is not None:
        df = state.retrieved_df
        final_message = {
            "role": "assistant", 
            "content": f"Data pipeline completed successfully! Final dataset: {df.shape[0]} rows × {df.shape[1]} columns"
        }
    else:
        final_message = {
            "role": "assistant",
            "content": "Pipeline completed but no data was retrieved."
        }
    
    state.messages.append(final_message)
    return state

def build_data_pipeline():
    """Build the orchestrated data pipeline"""
    builder = StateGraph(AppState)
    
    # Add nodes
    builder.add_node("retrieval", run_retrieval_stage)
    builder.add_node("preprocessing", run_preprocessing_stage)
    builder.add_node("finalize", finalize_pipeline)
    
    # Wire the graph
    builder.add_edge(START, "retrieval")
    
    # Conditional edge: preprocess only if we have data
    builder.add_conditional_edges(
        "retrieval",
        should_preprocess,
        {
            "preprocess": "preprocessing",
            "complete": "finalize"
        }
    )
    
    builder.add_edge("preprocessing", "finalize")
    builder.add_edge("finalize", END)
    
    return builder.compile()
