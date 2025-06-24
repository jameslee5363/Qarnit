from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd

@dataclass
class AgentState:
    # Raw user input
    question: str

    # Container for arbitrary data shared between agents
    data: Dict[str, Any] = field(default_factory=dict)

    # Collected messages or outputs from agents
    messages: List[str] = field(default_factory=list) # idk

    # Retriever outputs
    is_relevant: Optional[bool] = None
    parsed_question: Dict[str, Any] = field(default_factory=dict)
    sql_query: Optional[str] = None
    sql_valid: Optional[bool] = None
    sql_issues: Optional[str] = None

    raw_results: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_df: Optional[pd.DataFrame] = None

    # Preprocessor outputs (and intermediate)
    preprocessed_df: Optional[pd.DataFrame] = None
    preprocessing_code: Optional[str] = None
    preprocessing_errors: Optional[str] = None

    # Supervisor decision
    next_agents: List[str] = field(default_factory=list)

    @property
    def latest_user_input(self) -> str:
        """
        Alias for the last user-provided question or instruction.
        """
        return self.question

    def add_message(self, msg: str) -> None:
        """
        Append an output or informational message produced by an agent.
        """
        self.messages.append(msg)
