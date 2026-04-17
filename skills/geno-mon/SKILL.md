---
name: geno-mon
description: >-
  Agent observability — list sessions, view metrics, tail messages from other Claude Code sessions.
  Use when user says /geno-mon, wants to peek at another session, check session metrics,
  or see what another session is doing.
allowed-tools: "Bash(~/.geno/venv/bin/geno-mon *)"
argument-hint: "[list|tail|fork|<session-id>|--latest] [--json] [--project <name>]"
---

# geno-mon — Agent Observability

```!
which ~/.geno/venv/bin/geno-mon >/dev/null 2>&1 || echo "geno-mon is not installed. Run: pip install -e ~/code-purp/geno-mon-WS/geno-mon"
```

You have access to the geno-mon CLI at `~/.geno/venv/bin/geno-mon`. It parses Claude Code session logs from `~/.claude/projects/` and computes observability metrics.

## Commands

Parse the user's arguments to determine the action:

### `/geno-mon` (no args) or `/geno-mon list`
List available sessions. Run:
```bash
~/.geno/venv/bin/geno-mon list
```
Display the output directly — it shows session index, project, ID prefix, and age.

To filter by project:
```bash
~/.geno/venv/bin/geno-mon list --project <name>
```

### `/geno-mon <session>`
Analyze a specific session. The argument can be:
- A **number** (index from `list`, e.g. `3` = 3rd most recent)
- A **partial session ID** (e.g. `d2cf72cc`)
- A **full JSONL path**

Run:
```bash
~/.geno/venv/bin/geno-mon <session>
```
This prints loop efficiency, tool use patterns, context/cache stats, and planning signals.

### `/geno-mon --latest`
Analyze the most recent session (shorthand for `-n 1`):
```bash
~/.geno/venv/bin/geno-mon --latest
```

### `/geno-mon tail [session]`
Show the last messages from a session — what it's been doing recently:
```bash
~/.geno/venv/bin/geno-mon tail                        # latest session, last 10
~/.geno/venv/bin/geno-mon tail <session> --last 20    # specific session, last 20
```
This shows timestamped user messages, assistant text, and tool calls with their key arguments.

### `/geno-mon fork [session]`
Extract the full context of a session as a markdown document, suitable for starting a new session that continues the work. This is essentially "forking" a session.

```bash
~/.geno/venv/bin/geno-mon fork                          # fork latest session
~/.geno/venv/bin/geno-mon fork <session>                 # fork specific session
~/.geno/venv/bin/geno-mon fork <session> -o context.md   # write to file
~/.geno/venv/bin/geno-mon fork <session> -m 20           # limit to last 20 user messages
```

The output includes:
- **Environment**: cwd, git branch, model
- **Files modified/read**: all files the session touched
- **Commands run**: unique shell commands executed
- **Conversation history**: user messages with assistant responses and tool usage

To fork into a new session, pipe the output or copy the file content as the first message in a new Claude Code session.

### `/geno-mon tail --json`
Same as tail but structured JSON output:
```bash
~/.geno/venv/bin/geno-mon tail --json
~/.geno/venv/bin/geno-mon tail <session> --last 20 --json
```

### JSON output
Any command can add `--json` for structured output:
```bash
~/.geno/venv/bin/geno-mon list --json
~/.geno/venv/bin/geno-mon --latest --json
~/.geno/venv/bin/geno-mon <session> --json
```

## Interpreting Results

When showing results to the user, highlight:
- **Thrashing score > 0.3** — the session may be stuck in a loop
- **Error recovery > 5** — lots of errors being recovered from
- **Cache hit rate < 80%** — inefficient context reuse
- **Hot resources** — files being accessed repeatedly (possible sign of struggle)
- **Tool diversity** — low diversity means heavy reliance on few tools

For `tail` output, summarize what the session is currently working on based on the recent messages and tool calls.
