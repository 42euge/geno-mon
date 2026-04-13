"""Data models for parsed agent sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0

    @property
    def total_input(self) -> int:
        """Total input tokens including cache."""
        return self.input_tokens + self.cache_read_tokens + self.cache_creation_tokens

    @property
    def total(self) -> int:
        return self.total_input + self.output_tokens

    @classmethod
    def from_raw(cls, usage: dict[str, Any]) -> TokenUsage:
        return cls(
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            cache_read_tokens=usage.get("cache_read_input_tokens", 0),
            cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
        )


@dataclass
class ToolCall:
    tool_id: str
    tool_name: str
    input: dict[str, Any]
    result: str | None = None
    duration_ms: int | None = None
    caller: str | None = None

    @property
    def is_error(self) -> bool:
        if self.result is None:
            return False
        r = self.result.lower()
        return "error" in r or "failed" in r or "rejected" in r


@dataclass
class ContentBlock:
    type: str  # "text", "thinking", "tool_use", "tool_result"
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Turn:
    role: str  # "user" or "assistant"
    timestamp: datetime
    uuid: str
    parent_uuid: str | None = None
    content_blocks: list[ContentBlock] = field(default_factory=list)
    usage: TokenUsage | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_use(self) -> bool:
        return len(self.tool_calls) > 0

    @property
    def text_content(self) -> str:
        parts = []
        for block in self.content_blocks:
            if block.type == "text":
                parts.append(block.data.get("text", ""))
        return "\n".join(parts)


@dataclass
class SubagentSpawn:
    agent_id: str
    parent_tool_use_id: str
    prompt: str
    subagent_type: str = "general-purpose"
    timestamp: datetime | None = None


@dataclass
class Session:
    session_id: str
    project: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    model: str = ""
    version: str = ""
    cwd: str = ""
    git_branch: str = ""
    turns: list[Turn] = field(default_factory=list)
    subagents: list[SubagentSpawn] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def user_turns(self) -> list[Turn]:
        return [t for t in self.turns if t.role == "user"]

    @property
    def assistant_turns(self) -> list[Turn]:
        return [t for t in self.turns if t.role == "assistant"]

    @property
    def all_tool_calls(self) -> list[ToolCall]:
        calls = []
        for turn in self.turns:
            calls.extend(turn.tool_calls)
        return calls

    @property
    def total_usage(self) -> TokenUsage:
        total = TokenUsage()
        for turn in self.assistant_turns:
            if turn.usage:
                total.input_tokens += turn.usage.input_tokens
                total.output_tokens += turn.usage.output_tokens
                total.cache_read_tokens += turn.usage.cache_read_tokens
                total.cache_creation_tokens += turn.usage.cache_creation_tokens
        return total
