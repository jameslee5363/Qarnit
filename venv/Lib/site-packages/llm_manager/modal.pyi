import requests
from enum import StrEnum
from llm_manager.cython import CythonBaseModel
from llm_manager.message import Message, MessageRole
from llm_manager.tools import Tools
from pydantic import BaseModel, Field
from typing import Any, Iterator

class LLMStatus(StrEnum):
    idle = "idle"
    answer = "answer"
    reason = "reason"
    tool_calls = "tool_calls"
    tool_results = "tool_results"

class ToolContent(BaseModel):
    name: str
    content: str | dict[str, Any]

class LLMResult(BaseModel):
    tool_calls: dict[str, ToolContent] = Field(default_factory=dict)
    tool_results: dict[str, ToolContent] = Field(default_factory=dict)
    reasoning_content: str = ""
    content: str = ""
    status: LLMStatus = LLMStatus.idle
    def __add__(self, other: "LLMResult") -> "LLMResult": ...

class LLModal(CythonBaseModel):
    section: str = "llm"
    endpoint_url: str = ""
    system_prompt: str = ""
    images: list[str] = Field(default_factory=list)
    video: list[str] = Field(default_factory=list)
    tools: Tools = Field(default_factory=Tools)
    messages: list[Message] = Field(default_factory=list)
    extra_body: dict[str, Any] = Field(default_factory=dict)
    retry: bool = False
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls_limit: int = 3
    _tool_calls_count: int = 0
    _close: bool = False
    _default: str = "The server is busy. Please try again later."
    def _reset(self) -> None: ...
    @property
    def stream(self) -> bool: ...
    @property
    def _extra_body(self) -> dict[str, Any]: ...
    @property
    def _headers(self) -> dict[str, str]: ...
    @property
    def _body(self) -> dict[str, Any]: ...
    @property
    def messages_latest(self) -> list[dict[str, Any]]: ...
    def message_latest(self, role: MessageRole) -> Message | None: ...
    def add_message(self, role: MessageRole, content: str) -> None: ...
    def _add_tool_calls(self, message: dict[str, Any]) -> None: ...
    def _message_process(self, message: dict[str, Any]) -> dict[str, str]: ...
    @staticmethod
    def _t_calls_beautify(tool_calls: list[dict[str, Any]]) -> dict[str, ToolContent]: ...
    @staticmethod
    def _t_results_beautify(tool_calls: dict[str, ToolContent], tool_results: list[Message]) -> dict[str, ToolContent]: ...
    def _response(self, response: requests.Response) -> LLMResult: ...
    def _stream_response(self, response: requests.Response) -> Iterator[LLMResult]: ...
    def _tool_calls(self) -> list[Message]: ...
    def _core_call(self) -> LLMResult | Iterator[LLMResult]: ...
    def invoke(self, prompt: str) -> LLMResult | Iterator[LLMResult]: ...
