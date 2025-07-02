import pandas as pd

def describe_dataframe_for_llm(df: pd.DataFrame) -> str:
    "Generates a detailed textual description of a DataFrame for a LLM."
    n_rows, n_cols = df.shape
    description = [f"The dataset contains {n_rows} rows and {n_cols} columns.\n"]

    # Types of columns
    type_counts = df.dtypes.value_counts()
    for dtype, count in type_counts.items():
        description.append(f"- {count} columns of type {dtype}.")
    description.append("")

    # Numerical Columns
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols):
        description.append("### Numerical columns:")
        for col in num_cols:
            desc = df[col].describe()
            description.append(
                f"- **{col}** : mean = {desc['mean']:.2f}, min = {desc['min']}, max = {desc['max']}, Standard deviation = {desc['std']:.2f}."
            )
    else:
        description.append("No numerical columns detected.")

    description.append("")

# Categorical or textual columns
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols):
        description.append("### Categorical columns :")
        for col in cat_cols:
            top = df[col].value_counts().head(3)
            description.append(f"- **{col}** : {len(df[col].unique())} Unique values. Top values: " + 
                               ", ".join([f"{val} ({cnt})" for val, cnt in top.items()]))
    else:
        description.append("No categorical columns detected.")

    description.append("")

    # Missing  Values 
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]
    if not missing_cols.empty:
        description.append("### Columns with missing values :")
        for col, count in missing_cols.items():
            description.append(f"- **{col}** : {count} Missing values ({count/n_rows:.1%})")
    else:
        description.append("No missing values detected.")

    return description
