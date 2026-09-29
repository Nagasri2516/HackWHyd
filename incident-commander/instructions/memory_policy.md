# Memory Policy (Hindsight)

This agent's intelligence comes from **Hindsight** — a memory layer that lets it remember,
recall, and improve over time. This file defines what we write to memory and how we read it.

## What we RETAIN (write to Hindsight)
Every time an incident is **resolved**, we store a durable postmortem memory:

- **World facts** — objective truth about the incident: service, error signature, root cause.
- **Experience facts** — what the agent/team *did* and whether it worked
  ("Rolling back the payments-api deploy cleared the 500s in 4 minutes").

Each memory carries a `context` tag (e.g. `postmortem:INC-2043`) and a `timestamp`, so
Hindsight can reason about *when* things happened and consolidate repeated patterns into
**observations** (e.g. "connection-pool exhaustion recurs on payments-api after traffic spikes").

## What we RECALL (read from Hindsight)
When a new incident arrives we call `recall(query=<symptoms + error signature>)`. Hindsight's
multi-strategy retrieval (keyword + vector + full-text + entity graph + temporal) returns the
most relevant past incidents, which we inject into the LLM prompt as grounding.

## What we REFLECT on
For trend questions ("what keeps breaking payments-api?") we call `reflect()`, which lets
Hindsight synthesize across many memories into higher-order observations.

## The learning loop
1. Incident arrives → **recall** similar past incidents.
2. Agent proposes a fix grounded in memory.
3. Incident resolved → **retain** the postmortem.
4. The next similar incident is diagnosed faster and more confidently.

This is why the agent is generic on day one and an expert by incident #20.
