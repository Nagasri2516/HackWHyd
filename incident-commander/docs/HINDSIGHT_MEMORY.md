# How Hindsight Memory Powers Incident Commander

> Required submission item: *"Explanation of how Hindsight memory is used in your solution."*

Hindsight (by Vectorize) is the agent-memory layer this project is built on. It gives the agent
three primitives — `retain`, `recall`, `reflect` — over a per-agent **memory bank**. Incident
Commander uses all three, and memory is the core of the product rather than an add-on.

## 1. `retain()` — turning postmortems into durable memory
Every time an incident is resolved (`agent.resolve_incident()`), we write **two** memories:

- A **world fact** — the objective record:
  `"[INC-2041] payments-api: HikariCP timeouts, connections maxed. Root cause: connection pool
  exhaustion under a 3x traffic spike. Resolution: killed idle-in-transaction backends, deployed
  PgBouncer."`
- An **experience fact** — what the team *did* and that it worked:
  `"[INC-2041] On payments-api, this WORKED: killing idle-in-transaction backends + PgBouncer."`

Each carries a `context` tag (`postmortem:INC-2041`) and a real `timestamp`, so Hindsight can
reason temporally and consolidate repeated patterns into **observations**.

Hindsight distinguishes World Facts from Experience Facts natively — we map our two memory kinds
onto exactly that model, which is why the agent can answer both *"what happened?"* and *"what
should I do?"*

## 2. `recall()` — grounding every diagnosis in the past
When a new incident arrives (`agent.handle_incident()`), we call
`recall(bank_id, query=<service + symptoms + error signature>)`. Hindsight's multi-strategy
retrieval (**TEMPR**: keyword + vector + full-text + entity graph + temporal, in parallel) returns
the most relevant past incidents. We inject them into the Groq prompt as grounding, and surface
them in the UI's Memory panel with relevance scores. The agent then leads with the resolution
that previously worked.

This is where simple vector search would fall short: *"what broke payments-api last July"* needs
temporal + entity reasoning, not just semantic similarity — exactly Hindsight's strength.

## 3. `reflect()` — consolidating incidents into insight
For trend questions (`agent.insights()`), we call `reflect(bank_id, query=...)`. Hindsight
synthesizes across many memories into higher-order **observations** — e.g. *"connection-pool
exhaustion recurs on payments-api after traffic spikes; PgBouncer is the durable fix."* This is
knowledge the agent was never explicitly told; it emerges from consolidated memory.

## The learning loop (why it gets better over time)
```
new incident ──▶ recall() similar past incidents ──▶ grounded fix (Groq)
      ▲                                                      │
      └──────────── retain() the postmortem ◀──── incident resolved
```
Interaction #1: generic. Interaction #5: recalls the exact runbook. Interaction #20: feels like
your most senior SRE. The seed set (8 postmortems) demonstrates this immediately; the "teach the
agent" flow lets judges extend it live.

## Where it lives in the code
- `incident_commander/memory/base.py` — the `retain/recall/reflect` interface.
- `incident_commander/memory/hindsight_store.py` — the real Hindsight SDK integration.
- `incident_commander/memory/local_store.py` — an offline, explainable fallback with the same API.
- `incident_commander/agent.py` — where the loop is wired.
- `instructions/memory_policy.md` — the human-readable policy for what we store and recall.

## Configuration
Set `MEMORY_BACKEND=hindsight` with `HINDSIGHT_API_URL` / `HINDSIGHT_API_KEY` to use a real
Hindsight instance (Cloud promo code **MEMHACK99** = $50 credits). With `auto`, the app uses
Hindsight when configured and the local fallback otherwise, so it always runs.
