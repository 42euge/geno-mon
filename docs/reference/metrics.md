# Metrics Reference

geno-mon computes four categories of metrics from parsed sessions.

## Loop Efficiency

| Metric | What it tells you |
|---|---|
| **Turns** | Total exchanges between user and agent. High counts may indicate a complex task or an agent struggling to converge. |
| **Tokens (in/out)** | Total token consumption. Input includes cache. Output is what the model generated. |
| **Tokens/turn** | Average context size per model call. Indicates how much context the agent is carrying. |
| **Tool calls** | Total tool invocations. Compare to turns to see how tool-heavy the session was. |
| **Error recovery** | Times the agent made a tool call immediately after a failed one. Indicates resilience vs thrashing. |

## Tool Use Patterns

| Metric | What it tells you |
|---|---|
| **Frequency** | Which tools the agent relies on most. Heavy Bash usage might indicate the agent isn't using dedicated tools. |
| **Diversity** | Unique tools / total calls. Low diversity means the agent is leaning on a few tools repeatedly. |
| **Subagents** | How many subagents were spawned. Indicates delegation behavior. |
| **Avg duration** | Mean time between tool call and result. Excludes outliers >10 min (likely user idle time). |

## Context & Cache

| Metric | What it tells you |
|---|---|
| **Cache hit rate** | Percentage of input tokens served from cache vs freshly computed. Higher is more efficient. |
| **Peak context** | Maximum input tokens in any single turn. Shows the ceiling of context usage. |
| **Context growth** | Change from first to last turn's context size. Positive means the agent is accumulating context. |

## Planning Signals

| Metric | What it tells you |
|---|---|
| **Thinking blocks** | Number of extended thinking blocks. More thinking generally correlates with more deliberate behavior. |
| **Thrashing score** | Proportion of tool calls targeting resources accessed 3+ times. High scores suggest the agent is revisiting the same files repeatedly without converging. |
| **Hot resources** | The most-accessed resources. Helps identify where the agent spent its effort — or where it got stuck. |

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
The agent is stuck in a loop — reading the same files, hitting errors, retrying.

### Exploratory session
```
Tool diversity:  high (30%+)
Subagents:       3+
Thrashing:       moderate (0.2-0.4)
Thinking blocks: many
```
Not necessarily bad — the agent is exploring broadly. Some thrashing is expected when exploring.

### Token-heavy but efficient
```
Tokens:          very high
Cache hit rate:  >95%
Tokens/turn:     high but stable
Thrashing:       low
```
Large session but well-managed. High cache hit rate means the agent is reusing context rather than rebuilding it.
