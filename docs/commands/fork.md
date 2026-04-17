# geno-mon fork

Extract a session's full context as a structured markdown document, suitable for "forking" the session — starting a new Claude Code session that continues where the original left off.

## Usage

```bash
geno-mon fork                            # fork latest session
geno-mon fork <session>                   # fork specific session
geno-mon fork <session> -o context.md     # write to file
geno-mon fork <session> -m 20            # limit to last 20 user messages
```

## What it extracts

The fork output is a structured markdown document with these sections:

### Environment

The session's working directory, git branch, and model.

```markdown
## Environment

- **Working directory:** `/Users/you/code/my-project`
- **Git branch:** `feat/new-feature`
- **Model:** claude-opus-4-6
```

### Files Modified

All files the session edited or created, tagged accordingly.

```markdown
## Files Modified

- `/src/parser.py` (edited)
- `/src/new_module.py` (created)
```

### Files Read

Files that were read but not modified — useful for understanding what context the session gathered.

```markdown
## Files Read

- `/src/models.py`
- `/tests/test_parser.py`
```

### Commands Run

Unique shell commands executed during the session (last 30, deduplicated).

```markdown
## Commands Run

- `python -m pytest tests/`
- `git status`
- `ls src/`
```

### Conversation History

The full conversation — user messages with assistant responses and tool usage summaries.

```markdown
### User [14:22:05]

fix the failing test in parser.py

**Assistant [14:22:12]:**

Let me look at the test failures.

*Tools used: `Read`(/src/tests/test_parser.py), `Edit`(/src/parser.py)*
```

## Options

| Flag | Description |
|---|---|
| `-o <file>`, `--output <file>` | Write output to a file instead of stdout |
| `-m <N>`, `--max-messages <N>` | Maximum user messages to include (default: 50) |
| `--project <name>` | Filter sessions by project name |

## How to fork a session

1. Extract the context:
   ```bash
   geno-mon fork <session> -o context.md
   ```

2. Start a new Claude Code session and paste the context as your first message, prefixed with instructions:
   ```
   Continue the work described in this context. Here's what the previous session was doing:

   <paste context.md contents>
   ```

3. The new session now has full awareness of what was done, which files were touched, and where the work left off.

## Use cases

- **Session continuation** — pick up where a session left off after it ended or was interrupted
- **Handoff** — pass session context to a different model or agent configuration
- **Knowledge transfer** — share what a session accomplished with other agents or team members
- **Debugging** — extract a full record of what happened in a session for analysis
