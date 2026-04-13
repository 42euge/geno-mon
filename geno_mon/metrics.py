"""Metrics computed from parsed agent sessions."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .models import Session, TokenUsage


@dataclass
class LoopEfficiency:
    total_turns: int = 0
    user_turns: int = 0
    assistant_turns: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_per_turn: float = 0.0
    session_duration_seconds: float | None = None
    tool_calls_total: int = 0
    error_recovery_count: int = 0


@dataclass
class ToolUsePatterns:
    tool_frequency: dict[str, int] = field(default_factory=dict)
    tool_sequence: list[str] = field(default_factory=list)
    tool_diversity: float = 0.0
    subagent_count: int = 0
    avg_tool_duration_ms: float | None = None


@dataclass
class ContextMemory:
    cache_hit_rate: float = 0.0
    context_growth: list[int] = field(default_factory=list)
    peak_context: int = 0
    total_cache_read: int = 0
    total_cache_creation: int = 0


@dataclass
class PlanningSignals:
    thinking_blocks: int = 0
    thrashing_score: float = 0.0
    thrashing_details: dict[str, int] = field(default_factory=dict)


@dataclass
class SessionMetrics:
    loop: LoopEfficiency = field(default_factory=LoopEfficiency)
    tools: ToolUsePatterns = field(default_factory=ToolUsePatterns)
    context: ContextMemory = field(default_factory=ContextMemory)
    planning: PlanningSignals = field(default_factory=PlanningSignals)


def compute_metrics(session: Session) -> SessionMetrics:
    """Compute all metrics from a parsed session."""
    metrics = SessionMetrics()

    _compute_loop_efficiency(session, metrics.loop)
    _compute_tool_patterns(session, metrics.tools)
    _compute_context_memory(session, metrics.context)
    _compute_planning_signals(session, metrics.planning)

    return metrics


def _compute_loop_efficiency(session: Session, loop: LoopEfficiency) -> None:
    loop.total_turns = len(session.turns)
    loop.user_turns = len(session.user_turns)
    loop.assistant_turns = len(session.assistant_turns)

    usage = session.total_usage
    loop.total_tokens = usage.total
    loop.input_tokens = usage.total_input
    loop.output_tokens = usage.output_tokens

    if loop.assistant_turns > 0:
        loop.tokens_per_turn = loop.total_tokens / loop.assistant_turns

    loop.session_duration_seconds = session.duration_seconds

    all_calls = session.all_tool_calls
    loop.tool_calls_total = len(all_calls)

    # Error recovery: count tool calls that immediately follow a failed tool call
    prev_was_error = False
    for turn in session.turns:
        if turn.role == "assistant" and prev_was_error and turn.has_tool_use:
            loop.error_recovery_count += 1
        # Check if this turn contains error results
        if turn.role == "user":
            for tc_block in turn.content_blocks:
                if tc_block.type == "tool_result":
                    result = tc_block.data.get("content", "")
                    if isinstance(result, list):
                        result = " ".join(
                            c.get("text", "") for c in result if isinstance(c, dict)
                        )
                    if isinstance(result, str) and (
                        "error" in result.lower()
                        or "failed" in result.lower()
                        or "rejected" in result.lower()
                    ):
                        prev_was_error = True
                        continue
            # If no error found in this user turn, reset
            if turn.role == "user":
                has_error = any(
                    _is_error_result(b) for b in turn.content_blocks if b.type == "tool_result"
                )
                prev_was_error = has_error


def _is_error_result(block) -> bool:
    result = block.data.get("content", "")
    if isinstance(result, list):
        result = " ".join(c.get("text", "") for c in result if isinstance(c, dict))
    if isinstance(result, str):
        r = result.lower()
        return "error" in r or "failed" in r or "rejected" in r
    return False


def _compute_tool_patterns(session: Session, tools: ToolUsePatterns) -> None:
    all_calls = session.all_tool_calls
    freq = Counter(tc.tool_name for tc in all_calls)
    tools.tool_frequency = dict(freq.most_common())
    tools.tool_sequence = [tc.tool_name for tc in all_calls]

    total = len(all_calls)
    unique = len(freq)
    tools.tool_diversity = unique / total if total > 0 else 0.0

    tools.subagent_count = len(session.subagents)

    # Filter out durations > 10 min (likely user idle time, not tool execution)
    max_reasonable_ms = 10 * 60 * 1000
    durations = [tc.duration_ms for tc in all_calls if tc.duration_ms is not None and tc.duration_ms < max_reasonable_ms]
    if durations:
        tools.avg_tool_duration_ms = sum(durations) / len(durations)


def _compute_context_memory(session: Session, ctx: ContextMemory) -> None:
    for turn in session.assistant_turns:
        if turn.usage:
            ctx.context_growth.append(turn.usage.total_input)
            ctx.total_cache_read += turn.usage.cache_read_tokens
            ctx.total_cache_creation += turn.usage.cache_creation_tokens

    if ctx.context_growth:
        ctx.peak_context = max(ctx.context_growth)

    total_cache = ctx.total_cache_read + ctx.total_cache_creation
    if total_cache > 0:
        ctx.cache_hit_rate = ctx.total_cache_read / total_cache


def _compute_planning_signals(session: Session, planning: PlanningSignals) -> None:
    # Count thinking blocks
    for turn in session.assistant_turns:
        for block in turn.content_blocks:
            if block.type == "thinking":
                planning.thinking_blocks += 1

    # Thrashing: repeated tool calls targeting the same resource
    resource_access: Counter[str] = Counter()
    for tc in session.all_tool_calls:
        # Identify the resource being accessed
        resource = _tool_call_resource(tc)
        if resource:
            resource_access[resource] += 1

    # Resources accessed 3+ times might indicate thrashing
    thrashing = {r: c for r, c in resource_access.items() if c >= 3}
    planning.thrashing_details = thrashing

    total_calls = len(session.all_tool_calls)
    if total_calls > 0 and thrashing:
        thrashing_calls = sum(thrashing.values())
        planning.thrashing_score = thrashing_calls / total_calls


def _tool_call_resource(tc) -> str | None:
    """Extract the resource identifier from a tool call."""
    inp = tc.input
    # File-based tools
    for key in ("file_path", "path", "file"):
        if key in inp:
            return str(inp[key])
    # Bash commands — use the command itself as resource
    if tc.tool_name == "Bash" and "command" in inp:
        return f"bash:{inp['command'][:80]}"
    # Grep/Glob — use pattern
    if tc.tool_name in ("Grep", "Glob") and "pattern" in inp:
        return f"{tc.tool_name.lower()}:{inp['pattern']}"
    return None
