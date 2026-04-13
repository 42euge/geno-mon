# geno-mon

**Agent observability for agentic harnesses.**

Most evaluations of AI agents focus on output quality — did the patch pass tests? Was the answer correct? But the *process* by which an agent arrives at a result is a black box.

geno-mon gives you insight into what's actually happening inside the agent loop.

---

## What it monitors

- **Loop efficiency** — turns, tokens, duration, error recovery
- **Tool use patterns** — frequency, sequence, diversity, subagent spawns
- **Context & cache** — cache hit rates, context growth, peak usage
- **Planning signals** — thinking blocks, thrashing detection

## Quick start

```bash
git clone https://github.com/42euge/geno-mon.git
cd geno-mon
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Then just run:

```bash
geno-mon
```

This opens an interactive session picker that lists your recent Claude Code sessions and shows full metrics for whichever you select.

## Usage

```
geno-mon                       # interactive session picker
geno-mon <path.jsonl>          # analyze a specific session
geno-mon list                  # list all available sessions
geno-mon --json                # machine-readable output
```

## Example output

```
── Session: d2cf72cc ────────────────────────────────────────

  Model:     claude-opus-4-6
  Duration:  48m 35s
  Branch:    main
  Version:   2.1.81

  Loop Efficiency
    Turns:          151 (65 user, 86 assistant)
    Tokens:         3.4M in / 24.2K out
    Tokens/turn:    40.3K
    Tool calls:     55
    Error recovery: 6

  Tool Use Patterns
    Bash                  27  ███████████████████████████
    Write                 10  ██████████
    Edit                   6  ██████
    Agent                  3  ███
    ToolSearch             3  ███
    AskUserQuestion        2  ██
    Subagents:       3
    Diversity:       16% (9 unique)
    Avg duration:    7008ms

  Context & Cache
    Peak context:    63.8K
    Cache hit rate:  98%
    Cache read:      3.4M
    Cache created:   81.2K
    Context growth:  +267%

  Planning Signals
    Thinking blocks: 7
    Thrashing score: 0.47
    Hot resources:
       11x  .../Documents/Everything
        5x  ...projects/-Users-euge-Library-Mobile-Documents
        4x  ...geno-mon/geno_mon/metrics.py
```

## Supported agents

Currently parses **Claude Code** JSONL session logs (`~/.claude/projects/`). Support for additional agent formats is planned.

## Part of the geno ecosystem

| Project | Role |
|---|---|
| [geno](https://github.com/42euge/geno) | Agent orchestrator |
| [geno-tools](https://github.com/42euge/geno-tools) | Skills package |
| **geno-mon** | Agent observability |
