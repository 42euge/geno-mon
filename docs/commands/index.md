# Commands

geno-mon is a single CLI binary with subcommands for different operations.

## Quick reference

| Command | Description |
|---|---|
| `geno-mon` | Interactive session picker |
| `geno-mon --latest` | Analyze the most recent session |
| `geno-mon -n 3` | Analyze the 3rd most recent session |
| `geno-mon <session>` | Analyze by partial ID, index, or file path |
| `geno-mon list` | [List all sessions](list.md) |
| `geno-mon tail` | [Show recent messages from a session](tail.md) |
| `geno-mon fork` | [Extract session context for forking](fork.md) |

## Session resolution

Most commands accept a `<session>` argument. This can be:

- **A number** (e.g. `3`) — the Nth most recent session from `list`
- **A partial session ID** (e.g. `d2cf72cc`) — matched against discovered sessions
- **A full JSONL path** — direct file path to a session log

If no session is specified, most commands default to the latest session.

## Global options

| Flag | Description |
|---|---|
| `--json` | Output as structured JSON (works with most commands) |
| `--project <name>` | Filter sessions by project name |
| `--latest`, `-l` | Shorthand for `-n 1` |
| `-n <N>` | Select the Nth most recent session |

## Interactive mode

Running `geno-mon` with no arguments opens an interactive picker:

```
$ geno-mon

Recent sessions:
    1. attention-bench-tasks            (2h ago)
    2. learning-bench                   (5h ago)
    3. google-deepmind-agi-hackathon    (1d ago)

Select session [1]:
```

Select a session to see its full metrics breakdown.
