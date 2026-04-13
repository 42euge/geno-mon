"""CLI for geno-mon agent observability."""

from __future__ import annotations

import json
from pathlib import Path

import click

from .metrics import SessionMetrics, compute_metrics
from .models import Session
from .parser import discover_sessions, parse_session


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "unknown"
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins}m"


def _format_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _shorten_project(slug: str, max_len: int = 40) -> str:
    """Make project slugs readable."""
    slug = slug.lstrip("-")
    parts = slug.split("-")
    # Drop common prefixes (Users, euge, Library, etc.)
    skip = {"Users", "euge", "Library", "Mobile", "Documents", "iCloud~md~obsidian"}
    filtered = [p for p in parts if p not in skip]
    result = "-".join(filtered)
    if len(result) > max_len:
        result = "..." + result[-(max_len - 3) :]
    return result


def _print_session_summary(session: Session, metrics: SessionMetrics) -> None:
    """Print a formatted session summary."""
    click.echo()
    click.secho(f"── Session: {session.session_id[:8]} ", fg="cyan", bold=True, nl=False)
    click.secho("─" * 40, fg="cyan")
    click.echo()

    # Metadata
    click.echo(f"  Model:     {session.model}")
    click.echo(f"  Duration:  {_format_duration(metrics.loop.session_duration_seconds)}")
    click.echo(f"  Branch:    {session.git_branch or 'n/a'}")
    click.echo(f"  Version:   {session.version}")
    click.echo()

    # Loop efficiency
    click.secho("  Loop Efficiency", fg="yellow", bold=True)
    click.echo(f"    Turns:          {metrics.loop.total_turns} ({metrics.loop.user_turns} user, {metrics.loop.assistant_turns} assistant)")
    click.echo(f"    Tokens:         {_format_tokens(metrics.loop.input_tokens)} in / {_format_tokens(metrics.loop.output_tokens)} out")
    click.echo(f"    Tokens/turn:    {_format_tokens(int(metrics.loop.tokens_per_turn))}")
    click.echo(f"    Tool calls:     {metrics.loop.tool_calls_total}")
    click.echo(f"    Error recovery: {metrics.loop.error_recovery_count}")
    click.echo()

    # Tool use
    click.secho("  Tool Use Patterns", fg="yellow", bold=True)
    for name, count in list(metrics.tools.tool_frequency.items())[:10]:
        bar = "█" * min(count, 30)
        click.echo(f"    {name:<20} {count:>3}  {bar}")
    if metrics.tools.subagent_count > 0:
        click.echo(f"    Subagents:       {metrics.tools.subagent_count}")
    diversity_pct = metrics.tools.tool_diversity * 100
    click.echo(f"    Diversity:       {diversity_pct:.0f}% ({len(metrics.tools.tool_frequency)} unique)")
    if metrics.tools.avg_tool_duration_ms is not None:
        click.echo(f"    Avg duration:    {metrics.tools.avg_tool_duration_ms:.0f}ms")
    click.echo()

    # Context
    click.secho("  Context & Cache", fg="yellow", bold=True)
    click.echo(f"    Peak context:    {_format_tokens(metrics.context.peak_context)}")
    click.echo(f"    Cache hit rate:  {metrics.context.cache_hit_rate * 100:.0f}%")
    click.echo(f"    Cache read:      {_format_tokens(metrics.context.total_cache_read)}")
    click.echo(f"    Cache created:   {_format_tokens(metrics.context.total_cache_creation)}")
    if metrics.context.context_growth:
        first = metrics.context.context_growth[0]
        last = metrics.context.context_growth[-1]
        if first > 0:
            growth = ((last - first) / first) * 100
            click.echo(f"    Context growth:  {growth:+.0f}%")
    click.echo()

    # Planning
    click.secho("  Planning Signals", fg="yellow", bold=True)
    click.echo(f"    Thinking blocks: {metrics.planning.thinking_blocks}")
    click.echo(f"    Thrashing score: {metrics.planning.thrashing_score:.2f}")
    if metrics.planning.thrashing_details:
        click.echo(f"    Hot resources:")
        for resource, count in sorted(
            metrics.planning.thrashing_details.items(), key=lambda x: -x[1]
        )[:5]:
            short = resource if len(resource) <= 60 else "..." + resource[-57:]
            click.echo(f"      {count:>3}x  {short}")
    click.echo()


def _metrics_to_dict(session: Session, metrics: SessionMetrics) -> dict:
    """Convert session + metrics to a JSON-serializable dict."""
    return {
        "session_id": session.session_id,
        "project": session.project,
        "model": session.model,
        "version": session.version,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "end_time": session.end_time.isoformat() if session.end_time else None,
        "loop": {
            "total_turns": metrics.loop.total_turns,
            "user_turns": metrics.loop.user_turns,
            "assistant_turns": metrics.loop.assistant_turns,
            "total_tokens": metrics.loop.total_tokens,
            "input_tokens": metrics.loop.input_tokens,
            "output_tokens": metrics.loop.output_tokens,
            "tokens_per_turn": round(metrics.loop.tokens_per_turn, 1),
            "session_duration_seconds": metrics.loop.session_duration_seconds,
            "tool_calls_total": metrics.loop.tool_calls_total,
            "error_recovery_count": metrics.loop.error_recovery_count,
        },
        "tools": {
            "frequency": metrics.tools.tool_frequency,
            "sequence": metrics.tools.tool_sequence,
            "diversity": round(metrics.tools.tool_diversity, 3),
            "subagent_count": metrics.tools.subagent_count,
            "avg_tool_duration_ms": metrics.tools.avg_tool_duration_ms,
        },
        "context": {
            "cache_hit_rate": round(metrics.context.cache_hit_rate, 3),
            "peak_context": metrics.context.peak_context,
            "context_growth": metrics.context.context_growth,
            "total_cache_read": metrics.context.total_cache_read,
            "total_cache_creation": metrics.context.total_cache_creation,
        },
        "planning": {
            "thinking_blocks": metrics.planning.thinking_blocks,
            "thrashing_score": round(metrics.planning.thrashing_score, 3),
            "thrashing_details": metrics.planning.thrashing_details,
        },
    }


def _interactive_picker(as_json: bool) -> None:
    """Interactive session picker."""
    sessions = discover_sessions()
    if not sessions:
        click.echo("No Claude Code sessions found in ~/.claude/projects/")
        return

    click.echo()
    click.secho("Recent sessions:", bold=True)
    click.echo()

    display = sessions[:20]
    for i, s in enumerate(display, 1):
        project = _shorten_project(s["project"])
        age = _format_age(s["modified_time"])
        click.echo(f"  {i:>3}. {project:<42} ({age})")

    click.echo()
    choice = click.prompt("Select session", type=int, default=1)

    if choice < 1 or choice > len(display):
        click.echo("Invalid selection.")
        return

    selected = display[choice - 1]
    session = parse_session(selected["path"])
    metrics = compute_metrics(session)

    if as_json:
        click.echo(json.dumps(_metrics_to_dict(session, metrics), indent=2))
    else:
        _print_session_summary(session, metrics)


def _format_age(dt) -> str:
    """Format a datetime as relative age."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    delta = now - dt
    seconds = delta.total_seconds()

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        m = int(seconds // 60)
        return f"{m}m ago"
    if seconds < 86400:
        h = int(seconds // 3600)
        return f"{h}h ago"
    days = int(seconds // 86400)
    if days == 1:
        return "yesterday"
    return f"{days}d ago"


@click.command()
@click.argument("path", required=False, type=click.Path(exists=False))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--project", "project_filter", help="Filter sessions by project name")
def main(path: str | None, as_json: bool, project_filter: str | None) -> None:
    """geno-mon — agent observability for agentic harnesses.

    Run without arguments for interactive session picker.
    Pass a session JSONL path to analyze directly.
    """
    # Handle "list" as a pseudo-subcommand
    if path == "list":
        sessions = discover_sessions(project_filter)
        if not sessions:
            click.echo("No sessions found.")
            return
        if as_json:
            click.echo(
                json.dumps(
                    [
                        {
                            "session_id": s["session_id"],
                            "project": s["project"],
                            "path": str(s["path"]),
                            "modified": s["modified_time"].isoformat(),
                        }
                        for s in sessions
                    ],
                    indent=2,
                )
            )
            return

        click.echo()
        click.secho("Available sessions:", bold=True)
        click.echo()
        for s in sessions[:30]:
            project = _shorten_project(s["project"])
            age = _format_age(s["modified_time"])
            click.echo(f"  {project:<42} {s['session_id'][:8]}  ({age})")
        click.echo()
        return

    # Handle "compare" as a pseudo-subcommand
    if path == "compare":
        click.echo("Usage: geno-mon compare <session1.jsonl> <session2.jsonl>")
        click.echo("Compare mode coming soon.")
        return

    # Direct path provided — parse and show metrics
    if path:
        p = Path(path)
        if not p.exists():
            click.echo(f"File not found: {path}")
            raise SystemExit(1)

        session = parse_session(p)
        metrics = compute_metrics(session)

        if as_json:
            click.echo(json.dumps(_metrics_to_dict(session, metrics), indent=2))
        else:
            _print_session_summary(session, metrics)
        return

    # No args — interactive picker
    _interactive_picker(as_json)


if __name__ == "__main__":
    main()
