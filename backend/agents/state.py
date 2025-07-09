from pydantic import BaseModel, Field, ConfigDict
import pandas as pd
from typing import List, Optional, Any, Dict

class AppState(BaseModel):
    """
    Top-level application state for the multi-agent chatbot.

    Tracks:
      - messages: List of message dicts (chat history)
      - data: Arbitrary data dict (e.g., DataFrame, code, etc.)
      - initial_question: The user's first retrieval query.
      - sql_queries: All SQL query strings executed.
      - retrieved_df: The final DataFrame retrieved from the database.
      - preprocessing_suggestion: Suggested preprocessing steps (str).
      - preprocessing_instruction: The user's chosen preprocessing instruction (str).
      - parsed_relevance: JSON result from relevance check (dict).
      - generated_code: Python code generated for preprocessing (str).
      - applied: Whether preprocessing code was applied successfully (bool).
      - extras: Optional dict for any other important variables.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True) #if you encounter a type you don't recognize, just accept it as-is without trying to validate or serialize it.(to handle pydantic errors)
    
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    initial_question: Optional[str] = None
    sql_queries: List[str] = Field(default_factory=list)
    retrieved_df: Optional[pd.DataFrame] = None
    preprocessing_suggestion: Optional[str] = None
    preprocessing_instruction: Optional[str] = None
    parsed_relevance: Optional[Dict[str, Any]] = None
    generated_code: Optional[str] = None
    applied: Optional[bool] = None
    extras: Dict[str, Any] = Field(default_factory=dict)

    def set_initial_question(self, question: str) -> None:
        self.initial_question = question
        self.messages.append({"role": "user", "content": question})

    def add_sql_query(self, query: str) -> None:
        self.sql_queries.append(query)

    def set_retrieved_df(self, df: pd.DataFrame) -> None:
        self.retrieved_df = df
        self.data['df'] = df

    def set_preprocessing_suggestion(self, suggestion: str) -> None:
        self.preprocessing_suggestion = suggestion

    def set_preprocessing_instruction(self, instruction: str) -> None:
        self.preprocessing_instruction = instruction
        self.messages.append({"role": "user", "content": instruction})

    def set_parsed_relevance(self, parsed: Dict[str, Any]) -> None:
        self.parsed_relevance = parsed

    def set_generated_code(self, code: str) -> None:
        self.generated_code = code
        self.data['generated_code'] = code

    def set_apply_result(self, success: bool) -> None:
        self.applied = success

    def record_extra(self, key: str, value: Any) -> None:
        self.extras[key] = value