"""Parse Claude Code JSONL session logs into structured data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    ContentBlock,
    Session,
    SubagentSpawn,
    TokenUsage,
    ToolCall,
    Turn,
)

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO 8601 timestamp from Claude Code logs."""
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def _extract_tool_calls(content_blocks: list[dict[str, Any]]) -> list[ToolCall]:
    """Extract tool_use blocks from message content."""
    calls = []
    for block in content_blocks:
        if block.get("type") == "tool_use":
            calls.append(
                ToolCall(
                    tool_id=block.get("id", ""),
                    tool_name=block.get("name", ""),
                    input=block.get("input", {}),
                    caller=block.get("caller", {}).get("type") if isinstance(block.get("caller"), dict) else None,
                )
            )
    return calls


def _extract_tool_results(content: list[dict[str, Any]]) -> dict[str, str]:
    """Extract tool_result blocks, keyed by tool_use_id."""
    results = {}
    for block in content:
        if block.get("type") == "tool_result":
            tool_use_id = block.get("tool_use_id", "")
            content_val = block.get("content", "")
            if isinstance(content_val, list):
                text_parts = [c.get("text", "") for c in content_val if isinstance(c, dict)]
                content_val = "\n".join(text_parts)
            results[tool_use_id] = content_val
    return results


def _parse_turn(entry: dict[str, Any]) -> Turn:
    """Parse a single log entry into a Turn."""
    msg = entry.get("message", {})
    content_raw = msg.get("content", [])

    if isinstance(content_raw, str):
        content_blocks = [ContentBlock(type="text", data={"text": content_raw})]
        tool_calls = []
    else:
        content_blocks = []
        for block in content_raw:
            if isinstance(block, dict):
                content_blocks.append(
                    ContentBlock(type=block.get("type", "unknown"), data=block)
                )
        tool_calls = _extract_tool_calls(content_raw)

    usage = None
    if msg.get("usage"):
        usage = TokenUsage.from_raw(msg["usage"])

    return Turn(
        role=entry.get("type", msg.get("role", "unknown")),
        timestamp=parse_timestamp(entry["timestamp"]),
        uuid=entry.get("uuid", ""),
        parent_uuid=entry.get("parentUuid"),
        content_blocks=content_blocks,
        usage=usage,
        tool_calls=tool_calls,
    )


def _link_tool_results(turns: list[Turn]) -> None:
    """Link tool_result messages back to their tool_use calls."""
    pending_calls: dict[str, ToolCall] = {}

    for turn in turns:
        # Register tool calls from assistant turns
        for tc in turn.tool_calls:
            pending_calls[tc.tool_id] = tc

        # Link results from user turns (tool results come back as user messages)
        if turn.role == "user":
            content = turn.content_blocks
            for block in content:
                if block.type == "tool_result":
                    tool_use_id = block.data.get("tool_use_id", "")
                    if tool_use_id in pending_calls:
                        result_content = block.data.get("content", "")
                        if isinstance(result_content, list):
                            text_parts = [
                                c.get("text", "")
                                for c in result_content
                                if isinstance(c, dict)
                            ]
                            result_content = "\n".join(text_parts)
                        pending_calls[tool_use_id].result = result_content


def _compute_tool_durations(turns: list[Turn]) -> None:
    """Compute tool call durations from timestamp gaps."""
    tool_call_times: dict[str, datetime] = {}

    for turn in turns:
        # Record when tool calls were made
        for tc in turn.tool_calls:
            tool_call_times[tc.tool_id] = turn.timestamp

        # When we see results, compute duration
        if turn.role == "user":
            for block in turn.content_blocks:
                if block.type == "tool_result":
                    tool_use_id = block.data.get("tool_use_id", "")
                    if tool_use_id in tool_call_times:
                        delta = turn.timestamp - tool_call_times[tool_use_id]
                        ms = int(delta.total_seconds() * 1000)
                        # Find the ToolCall and set duration
                        for t in turns:
                            for tc in t.tool_calls:
                                if tc.tool_id == tool_use_id:
                                    tc.duration_ms = ms


def _extract_subagents(turns: list[Turn], entries: list[dict[str, Any]]) -> list[SubagentSpawn]:
    """Extract subagent spawns from progress entries and tool calls."""
    subagents = []
    seen_ids: set[str] = set()

    # From progress entries
    for entry in entries:
        if entry.get("type") == "progress":
            data = entry.get("data", {})
            if data.get("type") == "agent_progress":
                agent_id = data.get("agentId", "")
                if agent_id and agent_id not in seen_ids:
                    seen_ids.add(agent_id)
                    subagents.append(
                        SubagentSpawn(
                            agent_id=agent_id,
                            parent_tool_use_id=entry.get("parentToolUseID", ""),
                            prompt=data.get("prompt", ""),
                            timestamp=parse_timestamp(entry["timestamp"]) if "timestamp" in entry else None,
                        )
                    )

    # Enrich with subagent_type from tool call inputs
    for turn in turns:
        for tc in turn.tool_calls:
            if tc.tool_name == "Agent":
                subagent_type = tc.input.get("subagent_type", "general-purpose")
                description = tc.input.get("description", "")
                prompt = tc.input.get("prompt", "")
                # Try to match by prompt
                for sa in subagents:
                    if sa.prompt == prompt or (description and description in sa.prompt):
                        sa.subagent_type = subagent_type
                        break

    return subagents


def _extract_project_name(path: Path) -> str:
    """Extract a readable project name from the session file path."""
    # Path pattern: ~/.claude/projects/<project-slug>/<session-id>.jsonl
    parts = path.parts
    try:
        projects_idx = parts.index("projects")
        slug = parts[projects_idx + 1]
        # Clean up the slug: strip leading dash, replace dashes with /
        slug = slug.lstrip("-")
        # Take the last meaningful segment
        segments = slug.split("-")
        # Find the last few meaningful segments
        return slug
    except (ValueError, IndexError):
        return path.parent.name


def parse_session(path: Path) -> Session:
    """Parse a Claude Code JSONL session log into a Session object."""
    entries: list[dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    turns: list[Turn] = []
    model = ""
    version = ""
    cwd = ""
    git_branch = ""
    session_id = ""

    for entry in entries:
        entry_type = entry.get("type", "")

        if entry_type in ("user", "assistant"):
            turn = _parse_turn(entry)
            turns.append(turn)

            # Extract session metadata from first available entry
            if not session_id:
                session_id = entry.get("sessionId", "")
            if not version:
                version = entry.get("version", "")
            if not cwd:
                cwd = entry.get("cwd", "")
            if not git_branch:
                git_branch = entry.get("gitBranch", "")

            # Model from assistant messages
            if entry_type == "assistant" and not model:
                model = entry.get("message", {}).get("model", "")

    # Link tool results to their calls
    _link_tool_results(turns)
    _compute_tool_durations(turns)

    # Extract subagents
    subagents = _extract_subagents(turns, entries)

    # Determine project name
    project = _extract_project_name(path)

    # Session timing
    start_time = turns[0].timestamp if turns else None
    end_time = turns[-1].timestamp if turns else None

    return Session(
        session_id=session_id or path.stem,
        project=project,
        start_time=start_time,
        end_time=end_time,
        model=model,
        version=version,
        cwd=cwd,
        git_branch=git_branch,
        turns=turns,
        subagents=subagents,
    )


def discover_sessions(project_filter: str | None = None) -> list[dict[str, Any]]:
    """Discover available Claude Code sessions.

    Returns list of dicts with: path, session_id, project, modified_time.
    """
    if not CLAUDE_PROJECTS_DIR.exists():
        return []

    sessions = []
    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        project_name = project_dir.name
        if project_filter and project_filter.lower() not in project_name.lower():
            continue

        for jsonl_file in project_dir.glob("*.jsonl"):
            sessions.append(
                {
                    "path": jsonl_file,
                    "session_id": jsonl_file.stem,
                    "project": project_name,
                    "modified_time": datetime.fromtimestamp(
                        jsonl_file.stat().st_mtime, tz=timezone.utc
                    ),
                }
            )

    sessions.sort(key=lambda s: s["modified_time"], reverse=True)
    return sessions
