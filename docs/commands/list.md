# geno-mon list

List all discovered Claude Code sessions, sorted by recency.

## Usage

```bash
geno-mon list
geno-mon list --project learning
geno-mon list --json
```

## Output

```
Available sessions:

    1. ~/code/attention-bench            d2cf72cc  (2h ago)
    2. ~/code/learning-bench             a1b2c3d4  (5h ago)
    3. ~/hackathon/deepmind              e5f6g7h8  (1d ago)
```

Each row shows:

- **Index** — use with other commands (e.g. `geno-mon 2`)
- **Project** — the working directory, shortened for display
- **Session ID** — first 8 characters (use with other commands)
- **Age** — how long ago the session was last modified

## Options

| Flag | Description |
|---|---|
| `--project <name>` | Filter sessions containing `<name>` in the project path (case-insensitive) |
| `--json` | Output as JSON array for scripting |

## JSON output

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
