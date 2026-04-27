# Getting Started

## Installation

```bash
geno-tools install geno-mon
```

Or from within an agent session:

```
/geno-tools install geno-mon
```

Requires Python 3.10+. The only runtime dependency is `click`.

## Your first run

Just run `geno-mon` with no arguments:

```
$ geno-mon

Recent sessions:
    1. attention-bench-tasks            (2h ago)
    2. learning-bench                   (5h ago)
    3. google-deepmind-agi-hackathon    (1d ago)

Select session [1]:
```

geno-mon discovers all agent sessions stored in `~/.claude/projects/` and lists them by recency. Pick one and you'll get a full metrics breakdown.

## Reading the output

The output is organized into four sections. Here's what to look at first:

### Loop Efficiency

The basics: how long was the session, how many turns, how many tokens. The key number here is **tokens/turn** — it tells you how much context the agent carried on average. High and rising means the agent is accumulating context without managing it.

**Error recovery** counts how many times the agent made a tool call right after a failure. A few is healthy (resilience). Many is a red flag (thrashing).

### Tool Use Patterns

A frequency breakdown of which tools the agent used. **Diversity** (unique tools / total calls) tells you whether the agent is using the right tool for each job or leaning on one tool for everything.

Heavy `Bash` usage in an agent session often means the agent is shelling out instead of using dedicated tools like `Read`, `Edit`, or `Grep`.

### Context & Cache

**Cache hit rate** shows how efficiently the agent reuses context across turns. 90%+ is typical for a well-structured session. Low hit rates mean the agent is constantly rebuilding context.

**Context growth** tracks how the context window fills over time. Positive growth means the agent accumulates state as it works.

### Planning Signals

**Thrashing score** is the proportion of tool calls targeting resources accessed 3+ times. It surfaces when the agent keeps revisiting the same files without converging. The **hot resources** list shows exactly which files are getting hammered.

## Other ways to run

```bash
# Analyze a specific session file directly
geno-mon ~/.claude/projects/<project-slug>/<session-id>.jsonl

# List all sessions (no interactive picker)
geno-mon list

# Filter sessions by project name
geno-mon list --project learning

# JSON output for scripting
geno-mon <path> --json
```

## Next steps

- [**Concepts**](concepts.md) — understand the data model and how metrics are computed
- [**User Guide**](guide.md) — full CLI reference and JSON schema
- [**Roadmap**](roadmap.md) — where geno-mon is heading
