# JSON Schema

The `--json` flag produces structured output you can pipe into other tools. Available on most commands.

## Session metrics

```bash
geno-mon <session> --json
geno-mon --latest --json
```

```json
{
  "session_id": "d2cf72cc-...",
  "project": "/Users/you/code/my-project",
  "model": "claude-opus-4-6",
  "version": "1.0.23",
  "start_time": "2026-04-13T06:05:23+00:00",
  "end_time": "2026-04-13T06:54:12+00:00",
  "loop": {
    "total_turns": 151,
    "user_turns": 65,
    "assistant_turns": 86,
    "total_tokens": 3424200,
    "input_tokens": 3400000,
    "output_tokens": 24200,
    "tokens_per_turn": 40300.0,
    "session_duration_seconds": 2915.0,
    "tool_calls_total": 55,
    "error_recovery_count": 6
  },
  "tools": {
    "frequency": {"Bash": 27, "Write": 10, "Edit": 6, "Read": 5},
    "sequence": ["Bash", "Write", "Bash", "Read", "..."],
    "diversity": 0.164,
    "subagent_count": 3,
    "avg_tool_duration_ms": 1250.0
  },
  "context": {
    "cache_hit_rate": 0.977,
    "peak_context": 63800,
    "context_growth": [12000, 18500, 25000, 63800],
    "total_cache_read": 3200000,
    "total_cache_creation": 200000
  },
  "planning": {
    "thrashing_score": 0.47,
    "thinking_blocks": 7,
    "thrashing_details": {
      "/src/parser.py": 4,
      "/src/models.py": 3
    }
  }
}
```

## Session list

```bash
geno-mon list --json
```

```json
[
  {
    "session_id": "d2cf72cc-1234-...",
    "project": "/Users/you/code/my-project",
    "path": "/Users/you/.claude/projects/-Users-you-code-my-project/d2cf72cc-1234-....jsonl",
    "modified": "2026-04-16T10:30:00+00:00"
  }
]
```

## Tail output

```bash
geno-mon tail --json
geno-mon tail <session> --last 20 --json
```

```json
[
  {
    "role": "user",
    "timestamp": "2026-04-16T14:22:05+00:00",
    "uuid": "msg-123...",
    "text": "fix the failing test in parser.py"
  },
  {
    "role": "assistant",
    "timestamp": "2026-04-16T14:22:12+00:00",
    "uuid": "msg-456...",
    "text": "Let me look at the test failures.",
    "tool_calls": [
      {"name": "Read", "id": "toolu_01Sj..."}
    ],
    "tokens": {"input": 28000, "output": 150}
  }
]
```
