# Roadmap

geno-mon is being built in deliberate phases. Each phase produces something useful on its own while laying the foundation for the next.

---

## Phase 1: Log Parser :white_check_mark:

**Status:** Complete

Parse Claude Code JSONL session logs into structured Python dataclasses.

- [x] JSONL reader with error tolerance
- [x] Data model: `Session`, `Turn`, `ToolCall`, `TokenUsage`, `SubagentSpawn`
- [x] Link `tool_use` → `tool_result` by ID
- [x] Compute tool call durations from timestamps
- [x] Extract subagent spawns from progress entries
- [x] Session discovery across `~/.claude/projects/`

## Phase 2: Metrics Framework :white_check_mark:

**Status:** Complete

Compute observability metrics from parsed sessions.

- [x] **Loop efficiency** — turns, tokens, tokens/turn, duration, tool calls, error recovery
- [x] **Tool use patterns** — frequency, sequence, diversity, subagent count, avg duration
- [x] **Context & cache** — cache hit rate, context growth, peak context
- [x] **Planning signals** — thinking blocks, thrashing score, hot resource detection
- [x] CLI with interactive picker, direct file analysis, JSON output

## Phase 3: Live Monitoring

**Status:** Planned

Hook into agent sessions in real-time rather than only analyzing after the fact.

Priorities:

- [ ] File watcher on active session JSONL (tail -f style)
- [ ] Streaming metrics that update as the session progresses
- [ ] Integration points for geno-tools hooks (pre/post tool call events)
- [ ] Lightweight — should not interfere with agent performance

!!! note "Architectural constraint"
    This phase will be introduced gradually. The parser and metrics layers are designed to work on partial data, so streaming should be additive rather than requiring a rewrite. We want the core parser/metrics to stay stable before adding real-time concerns.

## Phase 4: Visualization

**Status:** Planned

Dashboards and visual breakdowns of agent behavior.

Priorities:

- [ ] Session timeline — visual sequence of tool calls, thinking blocks, and errors
- [ ] Token usage over time — context growth curve, cache hit rate trend
- [ ] Tool use heatmap — which tools at which points in the session
- [ ] Cross-session comparison — how does the same task perform across models or agent versions
- [ ] Export to HTML for sharing

!!! note "Choosing what to visualize"
    We're intentionally deferring this phase until we have enough experience with the metrics to know which views actually provide insight vs just looking pretty. The JSON output from Phase 2 lets us experiment with ad-hoc visualization in notebooks before committing to a built-in dashboard.

## Future directions

These are ideas that may shape future work but aren't committed to yet:

**Multi-agent format support.** The `Session` model is designed to be format-agnostic. Adding parsers for Codex CLI, Cursor, Aider, or any agent that produces structured logs is a natural extension.

**Anomaly detection.** With enough session data, we can establish baselines for "normal" agent behavior and flag sessions that deviate — unusually high thrashing, excessive token usage, or error spirals.

**Cost estimation.** Map token usage to actual API pricing. Show users what each session costs and where the spend concentrates.

**Agent comparison framework.** Run the same task across different agents or models and produce a structured comparison of their process — not just output quality, but how they got there.

**Integration with benchmarks.** Connect geno-mon's process metrics with output-quality benchmarks (SWE-bench, Terminal-Bench, etc.) to answer: does a better process lead to better outcomes?
