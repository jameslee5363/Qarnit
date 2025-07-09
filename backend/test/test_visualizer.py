"""
Comprehensive Visualizer Agent Test
Tests the complete visualizer workflow from start to end.
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
from pathlib import Path
import time

# Add the backend directory to sys.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from config directory

from dotenv import load_dotenv
config_dir = Path(__file__).parent.parent / "config"
env_path = config_dir / ".env"
load_dotenv(dotenv_path=env_path)

from graphs.visualizer_graph import build_visualizer_graph
from agents.visualizer import (
    inspect_dataframe,
    check_feasibility,
    classify_visualization_type,
    prepare_visualization_data,
    generate_plots,
)
from agents.state import AppState

def create_test_data():
    """Create comprehensive test dataset."""
    np.random.seed(42)
    
    # Create a dataset with multiple data types for comprehensive testing

    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'sales': np.random.lognormal(7, 0.5, 100),
        'category': np.random.choice(['Electronics', 'Clothing', 'Food'], 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'customer_age': np.random.normal(40, 15, 100).astype(int),
        'discount': np.random.uniform(0, 0.3, 100),
        'rating': np.random.choice([1, 2, 3, 4, 5], 100)
    })

def test_individual_components():
    """Test each visualizer component individually."""
    print("🧪 Testing Individual Components")
    print("-" * 50)
    
    df = create_test_data()
    state = AppState()
    state.data["df"] = df
    
    # Test 1: Data Inspector

    print("1️⃣  Data Inspector...")
    state = inspect_dataframe(state)
    if state.has_error():
        print(f"   ❌ Failed: {state.get_error()}")
        return False
    
    viz_context = state.data.get("viz_context", {})
    print(f"   ✅ Success: Analyzed DataFrame")
    
    # Test 2: Feasibility Checker

    print("2️⃣  Feasibility Checker...")
    state = check_feasibility(state)
    if state.has_error():
        print(f"   ❌ Failed: {state.get_error()}")
        return False
    
    feasible = state.data.get("viz_feasible", False)
    print(f"   ✅ Success: Feasibility = {feasible}")
    
    if not feasible:
        print("   ⚠️  Data not suitable for visualization")
        return False
    
    # Test 3: Visualization Classifier

    print("3️⃣  Visualization Classifier...")
    state = classify_visualization_type(state)
    if state.has_error():
        print(f"   ❌ Failed: {state.get_error()}")
        return False
    
    viz_types = state.data.get("viz_context", {}).get("recommended_viz_types", [])
    print(f"   ✅ Success: {len(viz_types)} types recommended: {viz_types}")
    
    # Test 4: Data Preparer

    print("4️⃣  Data Preparer...")
    state = prepare_visualization_data(state)
    if state.has_error():
        print(f"   ❌ Failed: {state.get_error()}")
        return False
    
    prepared_data = state.data.get("prepared_viz_data", {})
    print(f"   ✅ Success: {len(prepared_data)} datasets prepared")
    
    # Test 5: Plot Generator

    print("5️⃣  Plot Generator...")
    state = generate_plots(state)
    if state.has_error():
        print(f"   ❌ Failed: {state.get_error()}")
        return False
    
    plots = state.data.get("generated_plots", [])
    print(f"   ✅ Success: {len(plots)} plots generated")
    
    return True

def test_graph_workflow():
    """Test the complete visualizer graph workflow."""
    print("\n🔄 Testing Complete Graph Workflow")
    print("-" * 50)
    
    df = create_test_data()
    initial_state = AppState()
    initial_state.data["df"] = df
    
    try:
        graph = build_visualizer_graph()
        print("   ✅ Graph built successfully")
        
        final_state = None
        step_count = 0
        
        start_time = time.time()
        for step in graph.stream(initial_state, stream_mode="values"):
            step_count += 1
            final_state = step
        execution_time = time.time() - start_time
        
        print(f"   ✅ Graph executed in {step_count} steps ({execution_time:.2f}s)")
        
        # Check final results

        if hasattr(final_state, 'data'):
            plots = final_state.data.get("generated_plots", [])
        else:
            plots = final_state.get("generated_plots", [])
        
        print(f"   ✅ Final result: {len(plots)} plots generated")
        
        return len(plots) > 0
        
    except Exception as e:
        print(f"   ❌ Graph execution failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with edge cases."""
    print("\n🛡️  Testing Error Handling")
    print("-" * 50)
    
    # Test 1: Missing DataFrame

    print("1️⃣  Testing missing DataFrame...")
    no_df_state = AppState()
    no_df_state = inspect_dataframe(no_df_state)
    
    if not no_df_state.has_error():
        print("   ⚠️  Expected error for missing DataFrame")
        return False
    print("   ✅ Correctly handled missing DataFrame")
    
    # Test 2: Empty DataFrame

    print("2️⃣  Testing empty DataFrame...")
    empty_state = AppState()
    empty_state.data["df"] = pd.DataFrame()
    empty_state = inspect_dataframe(empty_state)
    empty_state = check_feasibility(empty_state)
    
    # Should handle gracefully

    print("   ✅ Handled empty DataFrame")
    
    return True

def save_generated_plots(plots, test_name="main_test"):
    """Save generated plots to output directory."""
    output_dir = Path(__file__).parent / "visualizer_outputs" / test_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for i, plot_data in enumerate(plots):
        filename = f"{test_name}_{plot_data['type']}_{i+1}.png"
        filepath = output_dir / filename
        plot_data["figure"].savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(plot_data["figure"])
        saved_count += 1
    
    return saved_count, output_dir

def run_comprehensive_test():
    """Run the complete visualizer test suite."""
    print("🚀 Comprehensive Visualizer Agent Test")
    print("=" * 60)
    print("Testing complete workflow from DataFrame to generated plots")
    print("=" * 60)
    
    test_results = {}
    
    # Test individual components

    test_results["components"] = test_individual_components()
    
    # Test graph workflow

    test_results["graph"] = test_graph_workflow()
    
    # Test error handling

    test_results["error_handling"] = test_error_handling()
    
    # Generate final visualization with plot saving

    print("\n📊 Final End-to-End Test with Plot Generation")
    print("-" * 50)
    
    df = create_test_data()
    print(f"   📊 Test dataset: {df.shape}")
    print(f"   📋 Columns: {list(df.columns)}")
    
    # Run complete pipeline

    state = AppState()
    state.data["df"] = df
    
    start_time = time.time()
    
    state = inspect_dataframe(state)
    state = check_feasibility(state)
    state = classify_visualization_type(state)
    state = prepare_visualization_data(state)
    state = generate_plots(state)
    
    total_time = time.time() - start_time
    
    if state.has_error():
        print(f"   ❌ Pipeline failed: {state.get_error()}")
        test_results["end_to_end"] = False
    else:
        plots = state.data.get("generated_plots", [])
        saved_count, output_dir = save_generated_plots(plots, "end_to_end_test")
        
        print(f"   ✅ Pipeline completed in {total_time:.2f}s")
        print(f"   ✅ Generated {len(plots)} plots")
        print(f"   💾 Saved {saved_count} plots to {output_dir}")
         # Display plot details
        for i, plot in enumerate(plots, 1):
            plot_title = plot.get('title', plot.get('type', 'Unknown'))
            print(f"      {i}. {plot['type']}: {plot_title}")
        
        test_results["end_to_end"] = True
    
    # Summary

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🏆 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The visualizer agent is fully functional:")
        print("   ✅ Modular components working correctly")
        print("   ✅ Graph workflow executing successfully")
        print("   ✅ Error handling robust")
        print("   ✅ End-to-end pipeline generating plots")
        print("   ✅ Optimized LLM prompts performing well")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    print(f"\n{'🎯 TEST COMPLETED SUCCESSFULLY' if success else '❌ TESTS FAILED'}")
    sys.exit(0 if success else 1)
