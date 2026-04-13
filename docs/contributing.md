# Contributing & Development

## Getting started

```bash
git clone https://github.com/42euge/geno-mon.git
cd geno-mon
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Project structure

```
geno-mon/
├── pyproject.toml          # Package config, dependencies, entry point
├── mkdocs.yml              # Documentation site config
├── geno_mon/
│   ├── __init__.py
│   ├── cli.py              # Click-based CLI — entry point, display, formatting
│   ├── parser.py           # JSONL → dataclasses, session discovery
│   ├── models.py           # Dataclass definitions (Session, Turn, ToolCall, etc.)
│   └── metrics.py          # Metrics computed from a parsed Session
├── tests/
│   └── __init__.py
└── docs/                   # This website (mkdocs + Material)
```

## Architecture

The data flows through three layers:

```
JSONL file → parser.py → models.py (dataclasses) → metrics.py → cli.py (display)
```

1. **`parser.py`** reads raw JSONL and constructs a `Session` object with linked `Turn`s, `ToolCall`s, and `SubagentSpawn`s
2. **`models.py`** defines the data model — pure dataclasses with computed properties
3. **`metrics.py`** takes a `Session` and computes `SessionMetrics` (loop efficiency, tool patterns, context, planning)
4. **`cli.py`** handles all I/O — session discovery, interactive picker, formatted output, JSON serialization

Each layer only depends on the one before it. The CLI imports metrics and parser; metrics imports models; parser imports models.

## Key design decisions

**Dataclasses over dicts.** Parsed data is structured as typed dataclasses, not raw dicts. This makes the metrics layer reliable and the codebase self-documenting.

**No heavy dependencies.** The only runtime dependency is `click`. Everything else uses the standard library. This keeps the install fast and avoids version conflicts.

**CLI-first, library-implicit.** The primary interface is the CLI, but all modules are importable. You can `from geno_mon.parser import parse_session` in your own scripts.

**Metrics are computed, not stored.** Metrics are always derived fresh from the parsed session. No intermediate caching or state.

## Extension guides

### Adding a new metric

1. Add the field to the appropriate dataclass in `metrics.py` (`LoopEfficiency`, `ToolUsePatterns`, `ContextMemory`, or `PlanningSignals`)
2. Compute it in the corresponding `_compute_*` function
3. Add the display line in `cli.py` → `_print_session_summary()`
4. Add the field to `_metrics_to_dict()` for JSON output

??? example "Example: longest streak without errors"

    ```python
    # In metrics.py, add to LoopEfficiency:
    @dataclass
    class LoopEfficiency:
        # ... existing fields ...
        longest_clean_streak: int = 0

    # In _compute_loop_efficiency(), compute it:
    current_streak = 0
    max_streak = 0
    for turn in session.turns:
        if turn.role == "assistant" and turn.has_tool_use:
            has_error = any(tc.is_error for tc in turn.tool_calls)
            if not has_error:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
    loop.longest_clean_streak = max_streak
    ```

### Adding a new log format

To support a new agent (e.g., Codex CLI, Cursor):

1. Create a new parser file (e.g., `parser_codex.py`)
2. Implement a function that returns a `Session` object using the same dataclasses
3. In `cli.py`, detect the format (by file extension, content sniffing, or a `--format` flag) and route to the right parser

!!! info "Key constraint"
    All parsers must produce the same `Session` model. This keeps the metrics layer and CLI format-agnostic.

### Adding a CLI subcommand

The CLI uses Click. Pseudo-subcommands are dispatched via the `path` argument:

```python
if path == "my-command":
    # Handle it
    return
```

For more complex subcommands, consider migrating to `click.Group`.

## Running tests

```bash
source .venv/bin/activate
python -m pytest tests/
```

## Code style

- Type hints on all function signatures
- Dataclasses for structured data
- No classes where functions suffice
- Keep it simple — avoid abstractions until they're needed twice
