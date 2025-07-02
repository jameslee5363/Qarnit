from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any

class MessageRole(StrEnum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"

class Message(BaseModel):
    role: MessageRole
    contents: list[str | list[dict[str, Any]]] = Field(default_factory=list)
    tool_call_id: str = ""
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    @property
    def latest(self) -> dict[str, Any]: ...
    def __bool__(self) -> bool: ...
    def __repr__(self) -> str: ...
