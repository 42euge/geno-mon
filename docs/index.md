# geno-mon

## The agent process is a black box

Every benchmark for AI coding agents — SWE-bench, Terminal-Bench, MLE-bench — measures the same thing: **did the output pass?** But two agents can produce identical results through radically different processes. One plans deliberately, recovers from errors, and uses tools precisely. The other thrashes, brute-forces, and burns 10x the tokens getting there.

Nobody measures the process. **geno-mon does.**

---

## What you get

Run `geno-mon` and point it at any Claude Code session. In seconds you'll see:

- How many turns and tokens the agent used, and how efficiently
- Which tools it reached for and how often
- Whether it was planning or thrashing
- How well it managed context and cache
- Where it got stuck and how it recovered

```
── Session: d2cf72cc ────────────────────────────────────────

  Model:     claude-opus-4-6
  Duration:  48m 35s

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
    Subagents:       3
    Diversity:       16% (9 unique)

  Context & Cache
    Peak context:    63.8K
    Cache hit rate:  98%
    Context growth:  +267%

  Planning Signals
    Thinking blocks: 7
    Thrashing score: 0.47
    Hot resources:
        4x  ...geno_mon/metrics.py
        3x  ...geno_mon/models.py
```

## Quick start

```bash
git clone https://github.com/42euge/geno-mon.git
cd geno-mon
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
geno-mon
```

That's it. The interactive picker will list your recent sessions. Pick one and see what happened inside.

[:material-rocket-launch: Getting Started](getting-started.md){ .md-button .md-button--primary }
[:material-book-open-variant: Concepts](concepts.md){ .md-button }
[:material-github: View on GitHub](https://github.com/42euge/geno-mon){ .md-button }
