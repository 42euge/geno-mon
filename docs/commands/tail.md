# geno-mon tail

Show the last N messages from a session — what the agent was doing recently.

## Usage

```bash
geno-mon tail                          # latest session, last 10 messages
geno-mon tail <session>                # specific session
geno-mon tail <session> --last 20      # last 20 messages
geno-mon tail --json                   # structured JSON output
```

## Output

```
── Last 10 messages from d2cf72cc ──────────────────────────────

  [14:22:05] user: fix the failing test in parser.py
  [14:22:12] assistant: Let me look at the test failures.
  [14:22:12] → Read → /src/tests/test_parser.py
  [14:22:15] ← 1 tool result(s)
  [14:22:18] → Edit → /src/parser.py
  [14:22:20] ← 1 tool result(s)
  [14:22:23] assistant: Fixed the off-by-one error in parse_timestamp.
  [14:22:30] → Bash → python -m pytest tests/test_parser.py
  [14:22:35] ← 1 tool result(s)
  [14:22:38] assistant: All tests passing now.
```

Each line shows:

- **Timestamp** — when the message was sent
- **Role** — `user` or `assistant`
- **Content** — text messages are shown directly (truncated to 200 chars)
- **Tool calls** — shown as `→ ToolName → key argument`
- **Tool results** — shown as `← N tool result(s)`

## Options

| Flag | Description |
|---|---|
| `--last N`, `-L N` | Number of messages to show (default: 10) |
| `--json` | Output as structured JSON |

## JSON output

```bash
geno-mon tail --json
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

## Use cases

- **Check on a running session** — see what the agent is doing right now
- **Quick context** — understand what a session was about without reading the full metrics
- **Debugging** — trace the sequence of actions when something went wrong
