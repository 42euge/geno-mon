# Reference

## CLI reference

### `geno-mon` (no arguments)

Opens an interactive picker showing your most recent agent sessions. Select one to see its full metrics breakdown.

```
$ geno-mon

Recent sessions:
    1. attention-bench-tasks            (2h ago)
    2. learning-bench                   (5h ago)
    3. google-deepmind-agi-hackathon    (1d ago)

Select session [1]:
```

### `geno-mon <path>`

Analyze a specific session log file directly.

```bash
geno-mon ~/.claude/projects/<project-slug>/<session-id>.jsonl
```

### `geno-mon list`

List all available sessions without the interactive picker.

```bash
geno-mon list
geno-mon list --project learning    # filter by project name
```

### `geno-mon --json`

Output metrics as JSON for programmatic consumption. Works with all modes.

```bash
geno-mon <path> --json
geno-mon list --json
```

## Understanding the metrics

### Loop Efficiency

| Metric | What it tells you |
|---|---|
| **Turns** | Total exchanges between user and agent. High counts may indicate a complex task or an agent struggling to converge. |
| **Tokens (in/out)** | Total token consumption. Input includes cache. Output is what the model generated. |
| **Tokens/turn** | Average context size per model call. Indicates how much context the agent is carrying. |
| **Tool calls** | Total tool invocations. Compare to turns to see how tool-heavy the session was. |
| **Error recovery** | Times the agent made a tool call immediately after a failed one. Indicates resilience vs thrashing. |

### Tool Use Patterns

| Metric | What it tells you |
|---|---|
| **Frequency** | Which tools the agent relies on most. Heavy Bash usage might indicate the agent isn't using dedicated tools. |
| **Diversity** | Unique tools / total calls. Low diversity means the agent is leaning on a few tools repeatedly. |
| **Subagents** | How many subagents were spawned. Indicates delegation behavior. |
| **Avg duration** | Mean time between tool call and result. Excludes outliers >10 min (likely user idle time). |

### Context & Cache

| Metric | What it tells you |
|---|---|
| **Cache hit rate** | Percentage of input tokens served from cache vs freshly computed. Higher is more efficient. |
| **Peak context** | Maximum input tokens in any single turn. Shows the ceiling of context usage. |
| **Context growth** | Change from first to last turn's context size. Positive means the agent is accumulating context. |

### Planning Signals

| Metric | What it tells you |
|---|---|
| **Thinking blocks** | Number of extended thinking blocks. More thinking generally correlates with more deliberate behavior. |
| **Thrashing score** | Proportion of tool calls targeting resources accessed 3+ times. High scores suggest the agent is revisiting the same files repeatedly without converging. |
| **Hot resources** | The most-accessed resources. Helps identify where the agent spent its effort — or where it got stuck. |

## Where are session logs?

Session logs are stored at:

```
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

Subagent logs are in:

```
~/.claude/projects/<project-slug>/<session-id>/subagents/agent-<id>.jsonl
```

geno-mon automatically discovers all sessions in `~/.claude/projects/`.

## JSON output schema

The `--json` flag produces structured output you can pipe into other tools:

```json
{
  "session_id": "d2cf72cc-...",
  "project": "...",
  "model": "claude-opus-4-6",
  "start_time": "2026-04-13T06:05:23+00:00",
  "end_time": "2026-04-13T06:54:12+00:00",
  "loop": {
    "total_turns": 151,
    "tool_calls_total": 55,
    "error_recovery_count": 6
  },
  "tools": {
    "frequency": {"Bash": 27, "Write": 10},
    "sequence": ["Bash", "Write", "Bash"],
    "diversity": 0.164
  },
  "context": {
    "cache_hit_rate": 0.977,
    "peak_context": 63800
  },
  "planning": {
    "thrashing_score": 0.47
  }
}
```
