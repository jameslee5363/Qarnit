import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from pprint import pprint

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from config directory
from dotenv import load_dotenv
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
load_dotenv(dotenv_path=env_path)

from graphs.visualizer_graph import build_visualizer_graph
from agents.visualizer import (
    inspect_data,
    select_visualization_types,
    check_feasibility,
    prepare_visualization_data,
    generate_plots,
    validate_plots,
)

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
            if isinstance(value, pd.DataFrame):
                print(f"  {key}: DataFrame {value.shape}")
            elif isinstance(value, dict) and len(str(value)) > 200:
                print(f"  {key}: {type(value)} (large dict with {len(value)} keys)")
            else:
                print(f"  {key}: {type(value)} = {repr(value)}")
    
    # Show messages structure
    if "messages" in state:
        print(f"  messages: {len(state['messages'])} messages")
        for i, msg in enumerate(state["messages"]):
            print(f"    Message {i}: {type(msg).__name__}")
            if hasattr(msg, 'content'):
                content_preview = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                print(f"      Content: {content_preview}")

def create_test_data():
    """Create comprehensive test data for visualizer testing."""
    print_separator("Creating Test Data")
    
    np.random.seed(42)
    
    # Create test data with different types of columns
    data = {
        # Numerical columns
        'sales': np.random.normal(1000, 200, 100),
        'price': np.random.uniform(10, 100, 100),
        'quantity': np.random.randint(1, 50, 100),
        'profit': np.random.normal(150, 50, 100),
        
        # Categorical columns
        'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'status': np.random.choice(['Active', 'Inactive', 'Pending'], 100),
        
        # Date column
        'date': pd.date_range('2023-01-01', periods=100, freq='D'),
        
        # Mixed data with some missing values
        'rating': np.random.choice([1, 2, 3, 4, 5, np.nan], 100),
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values
    df.loc[df.sample(5).index, 'sales'] = np.nan
    df.loc[df.sample(3).index, 'category'] = np.nan
    
    print(f"Created test dataset with shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")
    
    return df

def test_individual_components():
    """Test each visualizer component individually."""
    print_separator("Testing Individual Components")
    
    # Create test data
    df = create_test_data()
    
    # Initialize state
    state = {
        "retrieved_df": df,
        "initial_question": "Analyze sales and customer data trends",
        "messages": []
    }
    
    # Test 1: Data Inspection
    print("\n1. Testing Data Inspection...")
    try:
        state = inspect_data(state)
        print("✓ Data inspection successful")
        if "data_description" in state:
            print(f"  Description length: {len(state['data_description'])} characters")
            print(f"  Description preview: {state['data_description'][:200]}...")
    except Exception as e:
        print(f"✗ Data inspection failed: {e}")
        return False
    
    inspect_state_structure(state, 1)
    
    # Test 2: Visualization Type Selection
    print("\n2. Testing Visualization Type Selection...")
    try:
        state = select_visualization_types(state)
        print("✓ Visualization type selection successful")
        if "visualization_types" in state:
            print(f"  Selected types: {state['visualization_types']}")
    except Exception as e:
        print(f"✗ Visualization type selection failed: {e}")
        return False
    
    inspect_state_structure(state, 2)
    
    # Test 3: Feasibility Check
    print("\n3. Testing Feasibility Check...")
    try:
        state = check_feasibility(state)
        print("✓ Feasibility check successful")
        if "viz_feasibility" in state:
            print(f"  Feasibility: {state['viz_feasibility']}")
        if "feasibility_details" in state:
            print(f"  Details: {state['feasibility_details']}")
    except Exception as e:
        print(f"✗ Feasibility check failed: {e}")
        return False
    
    inspect_state_structure(state, 3)
    
    # Test 4: Data Preparation
    print("\n4. Testing Data Preparation...")
    try:
        state = prepare_visualization_data(state)
        print("✓ Data preparation successful")
        if "prepared_viz_data" in state:
            print(f"  Prepared {len(state['prepared_viz_data'])} visualization types")
            for viz_type, data in state['prepared_viz_data'].items():
                print(f"    {viz_type}: {type(data)} with keys {list(data.keys())}")
    except Exception as e:
        print(f"✗ Data preparation failed: {e}")
        return False
    
    inspect_state_structure(state, 4)
    
    # Test 5: Plot Generation (may fail due to matplotlib dependencies)
    print("\n5. Testing Plot Generation...")
    try:
        state = generate_plots(state)
        print("✓ Plot generation successful")
        if "generated_plots" in state:
            print(f"  Generated {len(state['generated_plots'])} plots")
            for viz_type, plot in state['generated_plots'].items():
                print(f"    {viz_type}: {type(plot)}")
    except Exception as e:
        print(f"✗ Plot generation failed: {e}")
        print("  This may be due to matplotlib dependencies or display issues")
        # Don't return False here as plot generation might fail in headless environments
    
    inspect_state_structure(state, 5)
    
    # Test 6: Plot Validation
    print("\n6. Testing Plot Validation...")
    try:
        state = validate_plots(state)
        print("✓ Plot validation successful")
        if "plot_validation_results" in state:
            print(f"  Validation results available")
        if "visualization_complete" in state:
            print(f"  Visualization complete: {state['visualization_complete']}")
    except Exception as e:
        print(f"✗ Plot validation failed: {e}")
        return False
    
    inspect_state_structure(state, 6)
    
    return True

def test_visualizer_graph():
    """Test the complete visualizer graph."""
    print_separator("Testing Visualizer Graph")
    
    # Create test data
    df = create_test_data()
    
    # Initialize state
    initial_state = {
        "retrieved_df": df,
        "initial_question": "Analyze sales and customer data trends",
        "messages": []
    }
    
    try:
        # Build and run the graph
        graph = build_visualizer_graph()
        print("✓ Visualizer graph built successfully")
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        print("✓ Visualizer graph executed successfully")
        
        # Check final state
        print(f"\nFinal state keys: {list(final_state.keys())}")
        if "visualization_complete" in final_state:
            print(f"Visualization complete: {final_state['visualization_complete']}")
        
        if "messages" in final_state:
            print(f"Total messages: {len(final_state['messages'])}")
            for i, msg in enumerate(final_state["messages"]):
                if hasattr(msg, 'content'):
                    print(f"  Message {i+1}: {msg.content}")
        
        return True
        
    except Exception as e:
        print(f"✗ Visualizer graph failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_real_data():
    """Test with actual data file if available."""
    print_separator("Testing with Real Data")
    
    # Look for data files
    data_dir = Path(__file__).parent.parent / "data"
    data_files = []
    
    if data_dir.exists():
        for file in data_dir.glob("*.csv"):
            data_files.append(file)
    
    if not data_files:
        print("No CSV files found in data directory. Skipping real data test.")
        return True
    
    # Test with first available data file
    data_file = data_files[0]
    print(f"Testing with data file: {data_file}")
    
    try:
        df = pd.read_csv(data_file)
        print(f"Loaded data with shape: {df.shape}")
        
        # Limit to first 100 rows for faster testing
        if df.shape[0] > 100:
            df = df.head(100)
            print(f"Limited to first 100 rows for testing")
        
        # Initialize state
        state = {
            "retrieved_df": df,
            "initial_question": f"Analyze data from {data_file.name}",
            "messages": []
        }
        
        # Run data inspection and type selection
        state = inspect_data(state)
        state = select_visualization_types(state)
        state = check_feasibility(state)
        
        if state.get("viz_feasibility", False):
            state = prepare_visualization_data(state)
            print("✓ Real data test successful")
        else:
            print("✗ Real data is not feasible for visualization")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Real data test failed: {e}")
        return False

def main():
    """Main test function."""
    print_separator("VISUALIZER AGENT TESTS")
    
    tests = [
        ("Individual Components", test_individual_components),
        ("Visualizer Graph", test_visualizer_graph),
        ("Real Data", test_with_real_data),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✓ {test_name} TEST PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} TEST FAILED")
        except Exception as e:
            print(f"✗ {test_name} TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print_separator("TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
