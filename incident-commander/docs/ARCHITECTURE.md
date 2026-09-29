# Architecture

```
                         ┌──────────────────────────────────────────┐
   On-call engineer ──▶  │  Web console (FastAPI + vanilla JS)       │
   "checkout 503s!"      │  or CLI (incident_commander.cli)          │
                         └───────────────┬──────────────────────────┘
                                         │ description + service
                                         ▼
                         ┌──────────────────────────────────────────┐
                         │            IncidentAgent                  │
                         │  1. recall(query)  ───────────────┐       │
                         │  2. match runbooks (.md)           │       │
                         │  3. build grounded prompt          │       │
                         │  4. Groq LLM → structured answer   │       │
                         │  5. resolve_incident() → retain()  │       │
                         └───────┬───────────────────┬────────┘       
                                 │                   │                
                    instructions/*.md          MemoryStore (interface)
                    (system prompt,            ┌───────────┴───────────┐
                     playbook, runbooks)       ▼                       ▼
                                        HindsightMemory          LocalMemory
                                        (retain/recall/          (JSON + IDF
                                         reflect via SDK)         scoring, offline)
                                              │
                                              ▼
                                     Groq  (openai/gpt-oss-120b)
```

## Components

### `agent.py` — orchestration
The single brain. `handle_incident()` runs the **recall → reason → respond** path;
`resolve_incident()` runs the **retain** (learning) path; `insights()` calls **reflect**.
It assembles the LLM prompt from three grounding sources: the triage playbook, recalled
memories, and matched runbooks.

### `memory/` — the star, behind one interface
`MemoryStore` (base.py) defines `retain / recall / reflect / all_memories`. Two backends:
- `hindsight_store.py` wraps the `hindsight-client` SDK. Defensive normalization handles
  SDK response-shape differences across versions.
- `local_store.py` is a transparent fallback: IDF-weighted keyword overlap + service/entity
  boost + recency decay. Deterministic, so judges can *see why* a memory surfaced.
`factory.py` chooses the backend from `MEMORY_BACKEND` (auto/hindsight/local).

### `llm.py` — Groq with graceful degradation
`GroqLLM` retries 3× and surfaces clear errors. `FallbackLLM` templates a memory-grounded
answer when no key is present, so the app is always runnable.

### `instructions.py` — Markdown-defined behavior
Loads and caches the `.md` instruction files and does lightweight runbook matching. The
agent's personality and knowledge are editable without code.

### `web.py` / `web/` — the demo surface
A FastAPI app serving a single-page console. The right-hand **Memory panel** makes recall
visible in real time — the memory layer is literally the centerpiece of the UI.

## Data flow for one incident
1. User submits symptoms → `POST /api/incident`.
2. `recall()` returns top-k past incidents (shown in the Memory panel with scores).
3. Prompt = system prompt + playbook + recalled memories + runbooks + active incident.
4. Groq returns a structured response (assessment, root cause + confidence, actions, memory used).
5. User records the resolution → `retain()` writes two memories → the agent is now smarter.

## Design principles
- **Memory-first:** every UX decision surfaces what the agent remembered and why.
- **Runs anywhere:** offline fallbacks for both LLM and memory; real creds unlock full power.
- **Explainable:** recalled memories carry scores and IDs; the answer cites the memory it used.
- **Tight scope:** one persona (on-call SRE), one workflow (incident response), done well.
