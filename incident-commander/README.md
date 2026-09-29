# ◎ Incident Commander

**An AI Site Reliability Engineer that remembers every outage — so the next one is resolved in minutes, not hours.**

Built for the *AI Agents That Learn Using Hindsight* hackathon · Engineering & DevOps track.
Powered by **[Hindsight](https://hindsight.vectorize.io/)** (agent memory) + **[Groq](https://groq.com/)** (fast LLM).

---

## The problem
When production breaks at 2am, the on-call engineer is often re-solving an incident the team
already solved months ago — digging through Slack, old postmortems, and CRM-style runbooks
while the clock (and revenue) burns. **Institutional incident knowledge lives in people's heads
and forgotten docs.**

## The solution
Incident Commander is an agent with a persistent **memory of every past incident**. When a new
incident arrives it **recalls** the most similar past incidents from Hindsight, grounds a Groq
LLM in that history, and leads with *the fix that actually worked last time*. Every resolved
incident is **retained** back into memory — so the agent gets measurably sharper over time.

> **Without memory:** generic SRE advice.
> **With memory:** *"This matches INC-2041 and INC-2064 — connection-pool exhaustion under a
> traffic spike. Kill idle-in-transaction backends now, then roll out PgBouncer. That resolved
> it in ~5 minutes last time."*

This is the memory learning loop, and it maps directly to the rubric: memory is not a feature,
it's the whole product.

---

## Quickstart (runs offline in 60 seconds — no keys needed)

```bash
# 1. install
python -m venv .venv
.venv\Scripts\activate        # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# 2. see the "before vs. after memory" demo in your terminal
python -m incident_commander.cli demo

# 3. launch the web console (auto-seeds incident history)
python run.py
# open http://127.0.0.1:8000
```

The project ships with an **offline fallback** for both the LLM and memory, so it runs with
zero configuration. Add real credentials to unlock full power (below).

### Turn on Groq + Hindsight (recommended for the real demo)
```bash
cp .env.example .env        # then edit .env
```
```ini
GROQ_API_KEY=gsk_...                 # free at https://groq.com
GROQ_MODEL=openai/gpt-oss-120b       # or qwen/qwen3-32b
MEMORY_BACKEND=hindsight
HINDSIGHT_API_URL=https://...        # Hindsight Cloud or self-hosted
HINDSIGHT_API_KEY=...
HINDSIGHT_BANK_ID=incident-commander
```
> Hindsight Cloud promo code **MEMHACK99** = $50 free credits (add in billing after registering).

---

## How Hindsight memory is used (rubric: 25%)
The agent's intelligence *is* its memory. See [`instructions/memory_policy.md`](instructions/memory_policy.md)
and [`docs/HINDSIGHT_MEMORY.md`](docs/HINDSIGHT_MEMORY.md).

| Hindsight op | Where | What it does here |
|---|---|---|
| `retain()` | `agent.resolve_incident()` | Writes each postmortem as a **world fact** + an **experience fact** ("this WORKED: …"), tagged with `context` and `timestamp`. |
| `recall()` | `agent.handle_incident()` | Pulls the most similar past incidents for the active alert and injects them into the prompt. |
| `reflect()` | `agent.insights()` | Synthesizes trends across incidents ("what keeps breaking payments-api?") into observations. |

Swappable backends behind one interface (`incident_commander/memory/`):
- **`HindsightMemory`** — the required tech; real vector + entity-graph + temporal retrieval.
- **`LocalMemory`** — a transparent, dependency-free fallback so judges can run it instantly.

## Groq LLM (recommended tech)
`incident_commander/llm.py` uses the official `groq` SDK with **retry + graceful degradation**
(the docs warn to handle function-calling errors). Default model `openai/gpt-oss-120b`.

## All agent instructions live in Markdown
Per the plan, the agent's behavior is defined entirely in editable `.md` files:
`instructions/system_prompt.md`, `triage_playbook.md`, `memory_policy.md`, and
`instructions/runbooks/*.md`. Tune the agent without touching Python.

---

## Repository layout
```
incident-commander/
├── run.py                       # one-command launcher (seeds + serves web)
├── requirements.txt / .env.example
├── instructions/                # 🧠 agent brain, all Markdown
│   ├── system_prompt.md · triage_playbook.md · memory_policy.md
│   └── runbooks/*.md
├── incident_commander/
│   ├── config.py · instructions.py · llm.py · agent.py · seed.py · cli.py · web.py
│   └── memory/                   # base + hindsight_store + local_store + factory
├── web/                         # FastAPI single-page ops console (index/app.js/styles.css)
├── data/incidents.json          # 8 realistic synthetic postmortems
├── docs/                        # ARCHITECTURE · DEMO_SCRIPT · JUDGING · HINDSIGHT_MEMORY
├── content/                     # article · social post · video script (submission deliverables)
└── tests/test_smoke.py
```

## CLI reference
```bash
python -m incident_commander.cli seed         # load incident history into memory
python -m incident_commander.cli ask "<logs>" --service payments-api
python -m incident_commander.cli resolve --id INC-3001 --service ... --symptoms ... --cause ... --resolution ... --worked ...
python -m incident_commander.cli insights "what keeps breaking payments-api?"
python -m incident_commander.cli memories     # list stored memories
python -m incident_commander.cli demo         # before/after memory showcase
```

## Tests
```bash
pytest -q     # 5 smoke tests: empty recall, learning loop, seeding, runbook match, reflect
```

## License
MIT — build on it, put it on your LinkedIn, take it to interviews.
