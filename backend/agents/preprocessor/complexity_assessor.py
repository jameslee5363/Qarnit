import re
from typing import Dict, Tuple, Optional
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import llm

"""
Enhanced complexity assessor with LLM-based feasibility checks.
Provides both hardcoded rules and intelligent complexity analysis.
"""

def assess_complexity(code: str, context: dict, max_cardinality: int = 100):
    """
    Enhanced guard-rail against memory-bloat and performance-intensive operations.
    Checks for various risky patterns beyond just get_dummies.
    Returns: (is_safe: bool, warning: str)
    """
    unsafe_messages = []
    dataset_shape = context.get("dataset_shape", (0, 0))
    dataset_size_mb = context.get("dataset_size_mb", 0)
    card_map = context.get("cardinalities", {})
    
    # Check dataset size thresholds
    if dataset_size_mb > 1000:  # > 1GB
        unsafe_messages.append(f"Large dataset ({dataset_size_mb}MB) may cause memory issues")
    
    # Check for high cardinality get_dummies operations
    if "get_dummies" in code:
        for col, card in card_map.items():
            # Check both explicit column references and general get_dummies calls
            explicit_pattern = rf"get_dummies\([^,]*['\"]{col}['\"]"
            general_pattern = r"get_dummies\(df(?:,\s*columns\s*=\s*\[.*?\])?"
            
            if card > max_cardinality and (re.search(explicit_pattern, code) or re.search(general_pattern, code)):
                unsafe_messages.append(
                    f"Column '{col}' cardinality={card} > {max_cardinality}; "
                    "one-hot encoding may bloat memory."
                )
    
    # Check for memory-intensive operations
    memory_intensive_patterns = [
        (r"\.pivot_table\(", "pivot_table operations can be memory intensive"),
        (r"\.merge\(.*how\s*=\s*['\"]cross['\"]", "cross joins can explode memory usage"),
        (r"for\s+\w+\s+in\s+.*:\s*for\s+\w+\s+in", "nested loops can be time intensive"),
        (r"\.rolling\([^)]*window\s*=\s*\d{3,}", "large rolling windows can be memory intensive")
    ]
    
    for pattern, message in memory_intensive_patterns:
        if re.search(pattern, code, re.MULTILINE):
            unsafe_messages.append(message)
    
    # Check for operations that scale poorly with dataset size
    if dataset_shape[0] > 100000:  # > 100k rows
        risky_with_large_data = [
            (r"\.groupby\(.*\)\..*\.rolling\(", "groupby + rolling on large datasets can be slow"),
            (r"\.groupby\([^)]*\)\.agg\(.*\{.*\}.*\)", "complex groupby aggregations on large datasets"),
        ]
        
        for pattern, message in risky_with_large_data:
            if re.search(pattern, code, re.MULTILINE):
                unsafe_messages.append(f"{message} (dataset has {dataset_shape[0]:,} rows)")

    if unsafe_messages:
        return False, " ; ".join(unsafe_messages)
    return True, ""

def assess_llm_complexity(code: str, context: dict, 
                         memory_threshold_mb: int = 500, 
                         time_threshold_sec: int = 30) -> Tuple[bool, str, dict]:
    """
    Use LLM to assess time and memory complexity of preprocessing code.
    
    Args:
        code: The preprocessing code to analyze
        context: Dictionary containing dataset info (shape, dtypes, cardinalities, etc.)
        memory_threshold_mb: Maximum acceptable memory usage in MB
        time_threshold_sec: Maximum acceptable execution time in seconds
    
    Returns:
        Tuple of (is_feasible: bool, warning_message: str, analysis: dict)
    """
    
    # Extract relevant context information
    dataset_shape = context.get("dataset_shape", "Unknown")
    column_types = context.get("column_types", {})
    cardinalities = context.get("cardinalities", {})
    dataset_size_mb = context.get("dataset_size_mb", "Unknown")
    
    # Build context string for LLM
    context_info = f"""
Dataset Information:
- Shape: {dataset_shape}
- Size: {dataset_size_mb} MB
- Column Types: {column_types}
- High Cardinality Columns: {[(col, card) for col, card in cardinalities.items() if card > 50]}
"""
    
    # Create LLM prompt for complexity analysis
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system", 
            """You are an expert data engineer specializing in performance optimization and memory management. 
            Analyze the given pandas preprocessing code and provide accurate time and memory complexity estimates.

            ANALYSIS FRAMEWORK:
            1. Identify memory-intensive operations (get_dummies, pivot, merge, groupby with large groups)
            2. Calculate approximate memory multipliers for each operation
            3. Estimate execution time based on dataset size and operations
            4. Consider cumulative effects of chained operations
            
            THRESHOLDS:
            - Memory threshold: {memory_threshold_mb} MB
            - Time threshold: {time_threshold_sec} seconds
            
            OUTPUT FORMAT (JSON):
            {{
                "estimated_memory_mb": <number>,
                "estimated_time_seconds": <number>, 
                "memory_critical_operations": [<list of risky operations>],
                "time_critical_operations": [<list of slow operations>],
                "is_memory_feasible": <boolean>,
                "is_time_feasible": <boolean>,
                "optimization_suggestions": [<list of suggestions>]
            }}"""
        ),
        (
            "human",
            """Dataset Context:
{context_info}

Code to Analyze:
```python
{code}
```

Provide detailed complexity analysis within the thresholds: Memory ≤ {memory_threshold_mb}MB, Time ≤ {time_threshold_sec}s"""
        )
    ])
    
    try:
        # Get LLM analysis
        response = llm.invoke(prompt_template.format_messages(
            memory_threshold_mb=memory_threshold_mb,
            time_threshold_sec=time_threshold_sec,
            context_info=context_info,
            code=code
        ))
        
        # Parse LLM response (try to extract JSON)
        import json
        response_text = response.content.strip()
        
        # Try to extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            analysis = json.loads(json_text)
        else:
            # Fallback if JSON parsing fails
            analysis = {
                "estimated_memory_mb": "unknown",
                "estimated_time_seconds": "unknown",
                "memory_critical_operations": [],
                "time_critical_operations": [],
                "is_memory_feasible": True,
                "is_time_feasible": True,
                "optimization_suggestions": ["LLM response parsing failed"]
            }
        
        # Determine overall feasibility
        is_memory_feasible = analysis.get("is_memory_feasible", True)
        is_time_feasible = analysis.get("is_time_feasible", True)
        is_feasible = is_memory_feasible and is_time_feasible
        
        # Build warning message
        warnings = []
        if not is_memory_feasible:
            est_memory = analysis.get("estimated_memory_mb", "unknown")
            warnings.append(f"Memory risk: ~{est_memory}MB (limit: {memory_threshold_mb}MB)")
            
        if not is_time_feasible:
            est_time = analysis.get("estimated_time_seconds", "unknown")
            warnings.append(f"Time risk: ~{est_time}s (limit: {time_threshold_sec}s)")
            
        warning_message = "; ".join(warnings) if warnings else ""
        
        return is_feasible, warning_message, analysis
        
    except Exception as e:
        # Fallback on LLM failure
        return True, f"LLM complexity analysis failed: {str(e)}", {
            "error": str(e),
            "fallback": True
        }


def assess_comprehensive_complexity(code: str, context: dict, 
                                   max_cardinality: int = 100,
                                   memory_threshold_mb: int = 500,
                                   time_threshold_sec: int = 30) -> Tuple[bool, str, dict]:
    """
    Comprehensive complexity assessment combining hardcoded rules and LLM analysis.
    
    Args:
        code: The preprocessing code to analyze
        context: Dictionary containing dataset info
        max_cardinality: Maximum cardinality for get_dummies operations
        memory_threshold_mb: Maximum acceptable memory usage in MB  
        time_threshold_sec: Maximum acceptable execution time in seconds
    
    Returns:
        Tuple of (is_feasible: bool, warning_message: str, full_analysis: dict)
    """
    
    # Run original hardcoded complexity check
    hardcoded_safe, hardcoded_warning = assess_complexity(code, context, max_cardinality)
    
    # Run LLM-based complexity analysis
    llm_safe, llm_warning, llm_analysis = assess_llm_complexity(
        code, context, memory_threshold_mb, time_threshold_sec
    )
    
    # Combine results
    overall_safe = hardcoded_safe and llm_safe
    
    warnings = []
    if hardcoded_warning:
        warnings.append(f"Rule-based check: {hardcoded_warning}")
    if llm_warning:
        warnings.append(f"LLM analysis: {llm_warning}")
    
    combined_warning = "; ".join(warnings)
    
    # Build comprehensive analysis
    full_analysis = {
        "hardcoded_check": {
            "is_safe": hardcoded_safe,
            "warning": hardcoded_warning
        },
        "llm_analysis": llm_analysis,
        "overall_feasible": overall_safe,
        "assessment_timestamp": str(__import__("datetime").datetime.now())
    }
    
    return overall_safe, combined_warning, full_analysis