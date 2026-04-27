# Session Logs

## Where are they?

Session logs are stored at:

```
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

The `<project-slug>` is derived from the working directory path, with `/` replaced by `-` and prefixed with `-`. For example:

```
/Users/you/code/my-project
→ ~/.claude/projects/-Users-you-code-my-project/
```

Subagent logs are stored in a subdirectory of the session:

```
~/.claude/projects/<project-slug>/<session-id>/subagents/agent-<id>.jsonl
```

geno-mon automatically discovers all sessions in `~/.claude/projects/`.

## Log format

Each line in the JSONL file is a single JSON object representing one event. The key entry types are:

### User message

```json
{
  "type": "user",
  "timestamp": "2026-04-13T06:05:23.316Z",
  "sessionId": "d2cf72cc-...",
  "cwd": "/Users/you/code/my-project",
  "version": "1.0.23",
  "message": {
    "role": "user",
    "content": [
      {"type": "text", "text": "fix the bug in parser.py"}
    ]
  }
}
```

### Assistant message (with tool use)

```json
{
  "type": "assistant",
  "timestamp": "2026-04-13T06:05:30.123Z",
  "message": {
    "role": "assistant",
    "model": "claude-opus-4-6",
    "content": [
      {"type": "text", "text": "Let me look at the parser."},
      {
        "type": "tool_use",
        "id": "toolu_01Sj...",
        "name": "Read",
        "input": {"file_path": "/src/parser.py"}
      }
    ],
    "usage": {
      "input_tokens": 3,
      "cache_read_input_tokens": 28000,
      "cache_creation_input_tokens": 5000,
      "output_tokens": 150
    }
  }
}
```

### Tool result

Tool results come back as content in a user-type message:

```json
{
  "type": "user",
  "timestamp": "2026-04-13T06:05:32.456Z",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01Sj...",
        "content": "1\timport json\n2\tfrom pathlib import Path\n..."
      }
    ]
  }
}
```

### Subagent progress

```json
{
  "type": "progress",
  "timestamp": "2026-04-13T06:10:00.789Z",
  "parentToolUseID": "toolu_02Ab...",
  "data": {
    "type": "agent_progress",
    "agentId": "agent-abc123",
    "prompt": "Search for all test files..."
  }
}
```
