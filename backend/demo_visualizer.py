#!/usr/bin/env python3
"""
Quick demonstration of the visualizer agent's capabilities.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.visualizer import (
    inspect_data, select_visualization_types, check_feasibility,
    prepare_visualization_data, generate_plots, validate_plots
)
from graphs.visualizer_graph import build_visualizer_graph
import pandas as pd
import numpy as np

def create_demo_data():
    """Create a small demo dataset for visualization."""
    np.random.seed(42)
    
    # Create sample sales data
    data = {
        'date': pd.date_range('2023-01-01', periods=50, freq='D'),
        'sales': np.random.normal(1000, 200, 50),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 50),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 50),
        'profit': np.random.normal(150, 50, 50)
    }
    
    return pd.DataFrame(data)

def main():
    print("🎯 VISUALIZER AGENT DEMO")
    print("=" * 50)
    
    # Create demo data
    df = create_demo_data()
    print(f"📊 Created sample dataset with {df.shape[0]} rows and {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    
    # Test the graph
    print("\n🔧 Building visualizer graph...")
    graph = build_visualizer_graph()
    
    # Run the complete pipeline
    print("\n🚀 Running complete visualization pipeline...")
    
    initial_state = {
        "retrieved_df": df,
        "initial_question": "Show me sales trends by region and category",
        "messages": []
    }
    
    try:
        final_state = graph.invoke(initial_state)
        
        print("\n✅ Pipeline completed successfully!")
        print(f"   Generated {len(final_state.get('generated_plots', {}))} visualizations")
        print(f"   Visualization types: {final_state.get('visualization_types', [])}")
        print(f"   Visualization complete: {final_state.get('visualization_complete', False)}")
        
        # Show validation results
        validation_results = final_state.get('plot_validation_results', {})
        if validation_results:
            print("\n📈 Validation Results:")
            overall_score = validation_results.get('overall_quality_score', 0)
            print(f"   Overall Quality Score: {overall_score:.2f}/1.0")
            
            individual_results = validation_results.get('individual_results', {})
            for viz_type, result in individual_results.items():
                if isinstance(result, dict):
                    score = result.get('quality_score', 0)
                    print(f"   {viz_type}: {score:.2f}/1.0")
                else:
                    print(f"   {viz_type}: {result:.2f}/1.0")
        
        # Save plots if possible
        try:
            import matplotlib.pyplot as plt
            plots = final_state.get('generated_plots', {})
            
            if plots:
                print(f"\n💾 Saving {len(plots)} plots...")
                for i, (plot_type, fig) in enumerate(plots.items()):
                    filename = f"demo_plot_{i+1}_{plot_type}.png"
                    fig.savefig(filename, dpi=150, bbox_inches='tight')
                    print(f"   Saved: {filename}")
                
                plt.close('all')  # Clean up
                print("   All plots saved successfully!")
        except Exception as e:
            print(f"   Note: Could not save plots - {e}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
