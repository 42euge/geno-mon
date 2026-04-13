# Concepts

## The agent loop

An agentic coding session is a loop:

```
User sends a message
  → Agent thinks
  → Agent calls a tool (Read, Edit, Bash, etc.)
  → Tool returns a result
  → Agent thinks again
  → Agent calls another tool (or responds to the user)
  → ...
User sends another message
  → Loop continues
```

Each iteration through this loop is a **turn**. A session is a sequence of turns. geno-mon parses these turns and extracts signals about how the agent is behaving.

## Data model

geno-mon parses raw JSONL logs into a hierarchy of Python dataclasses:

```
Session
├── session_id, project, model, version
├── start_time, end_time
├── turns: list[Turn]
│   ├── role: "user" | "assistant"
│   ├── timestamp
│   ├── content_blocks: list[ContentBlock]
│   │   └── type: "text" | "thinking" | "tool_use" | "tool_result"
│   ├── tool_calls: list[ToolCall]
│   │   ├── tool_name, tool_id
│   │   ├── input (arguments passed to the tool)
│   │   ├── result (what the tool returned)
│   │   └── duration_ms (time from call to result)
│   └── usage: TokenUsage
│       ├── input_tokens, output_tokens
│       └── cache_read_tokens, cache_creation_tokens
└── subagents: list[SubagentSpawn]
    ├── agent_id, subagent_type
    └── prompt
```

The parser does two important linking steps:

1. **Tool call → result linking.** The agent sends a `tool_use` block; the result comes back in a later `tool_result` block. The parser matches them by ID so you can see the full round-trip.
2. **Duration computation.** The time between a `tool_use` and its corresponding `tool_result` gives you the wall-clock duration of that tool call.

## From raw logs to metrics

Here's how a single JSONL entry becomes a metric.

**Raw log entry** (assistant message with tool use):
```json
{
  "type": "assistant",
  "timestamp": "2026-04-13T06:30:29.316Z",
  "message": {
    "model": "claude-opus-4-6",
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_01Sj...",
        "name": "Read",
        "input": {"file_path": "/src/main.py"}
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

**What the parser extracts:**

- A `Turn` with role `"assistant"`, timestamp, and one `ToolCall` (name=`Read`, input=`/src/main.py`)
- A `TokenUsage` with 3 direct input + 28K cache read + 5K cache creation = 33K total input, 150 output
- The tool call is registered as pending, waiting for its result in a subsequent user turn

**What metrics compute from this:**

- `tool_frequency["Read"]` increments by 1
- `tool_sequence` appends `"Read"`
- `context_growth` records 33,003 for this turn
- `cache_hit_rate` updates: 28K read / (28K read + 5K creation) = 85% for this turn
- If `/src/main.py` was already accessed twice before, `thrashing_score` goes up

## Reading metrics together

Individual metrics tell you facts. Combinations tell you stories.

### Efficient session
```
Tokens/turn:    low and stable
Cache hit rate:  >90%
Context growth:  moderate
Thrashing:       <0.1
Error recovery:  0-2
```
The agent knows what it's doing. It's reusing context efficiently, not revisiting files, and rarely hitting errors.

### Agent struggling
```
Tokens/turn:    high and rising
Cache hit rate:  variable
Thrashing:       >0.3
Error recovery:  5+
Hot resources:   same file appearing 5+ times
```
The agent is stuck in a loop — reading the same files, hitting errors, retrying. The thrashing score and hot resources pinpoint exactly where.

### Exploratory session
```
Tool diversity:  high (30%+)
Subagents:       3+
Thrashing:       moderate (0.2-0.4)
Thinking blocks: many
```
Not necessarily bad — the agent is exploring broadly, delegating to subagents, and thinking through options. Some thrashing is expected when exploring. Context is what matters: was this a research task or a simple bug fix?

### Token-heavy but efficient
```
Tokens:          very high
Cache hit rate:  >95%
Tokens/turn:     high but stable
Thrashing:       low
```
Large session but well-managed. The high cache hit rate means the agent is reusing context rather than rebuilding it. This is what a long, productive session looks like.
