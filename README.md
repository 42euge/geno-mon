# geno-mon

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://42euge.github.io/geno-mon/)

Agent observability for agentic harnesses.

Most evaluations of AI agents focus on **output quality** — did the patch pass tests? Was the answer correct? But the *process* by which an agent arrives at a result is a black box. geno-mon gives you insight into what's actually happening inside the agent loop.

## What it monitors

- **Tool use patterns** — which tools are selected, how often, in what order
- **Agent loop efficiency** — turns, tokens, and time to complete tasks; error recovery behavior
- **Memory & context management** — how agents maintain and retrieve relevant context over long sessions
- **Planning quality** — task decomposition vs thrashing; does the agent plan or brute force?
- **Metacognitive signals** — does the agent know when to stop, retry, or ask for help?

## Installation

```bash
geno-tools install geno-mon
```

Or from within an agent session:

```
/geno-tools install geno-mon
```

## Part of the geno ecosystem

- [geno](https://github.com/42euge/geno) — agent orchestrator
- [geno-tools](https://github.com/42euge/geno-tools) — skills package
- **geno-mon** — agent observability (this repo)

## Status

Early development.
