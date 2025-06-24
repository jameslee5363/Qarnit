import pandas as pd
from .state import AgentState
from .preprocessor_agent import PreprocessorAgent
import numpy as np

# Set seed for reproducibility
np.random.seed(0)
n = 10

# Create a more complex DataFrame with diverse types, missing values, and outliers
df = pd.DataFrame({
    "price": [100, 200, None, 400, 5000, -50, np.nan, 150, 300, None],
    "quantity": [1, 2, 3, None, 5, 0, -1, np.nan, 10, 2],
    "category": np.random.choice(["A", "B", "C", None], size=n),
    "discount": np.random.choice([0, 5, 10, None], size=n),
    "date": pd.to_datetime(np.random.choice(pd.date_range("2025-01-01", "2025-06-01"), size=n)),
    "comment": np.random.choice(["good", "average", "poor", None], size=n),
    "flag": np.random.choice([True, False, None], size=n),
})

complex_df = df  # from above

# Step 2: Create AgentState with instruction
state = AgentState(
    question="Fill in missing values with 0 and normalize numeric columns; fill missing categorical with 'Unknown'; handle dates and booleans appropriately",
    retrieved_df=complex_df
)

# Step 3: Run the PreprocessorAgent
agent = PreprocessorAgent()
updated_state = agent.run(state)

# Step 4: Print results
print("\n=== Messages ===")
for msg in updated_state.messages:
    print(msg)

print("\n=== Transformed DataFrame ===")
print(updated_state.data.get("df"))
