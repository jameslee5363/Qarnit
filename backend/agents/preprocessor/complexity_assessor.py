import re

def assess_complexity(code: str, context: dict, max_cardinality: int = 100):
    """
    Guard-rail against memory-bloat operations.
    If code calls pd.get_dummies on a column whose cardinality > max_cardinality,
    flag it as unsafe.
    Returns: (is_safe: bool, warning: str)
    """
    unsafe_messages = []

    # Only check if get_dummies appears in the code
    if "get_dummies" in code:
        # Pull in the map of column→cardinality from our context
        card_map = context.get("cardinalities", {})

        # Check each column's cardinality against the max
        for col, card in card_map.items():
            pattern = rf"get_dummies\([^,]*['\"]{col}['\"]"

            # If the column's cardinality is greater than the max, and the code calls get_dummies on it, flag it as unsafe
            if card > max_cardinality and re.search(pattern, code):
                unsafe_messages.append(
                    f"Column '{col}' cardinality={card} > {max_cardinality}; "
                    "one-hot encoding may bloat memory."
                )

    if unsafe_messages:
        return False, " ; ".join(unsafe_messages)
    return True, ""