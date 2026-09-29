# Demo Script (90 seconds to a "wow")

Goal: make judges *feel* the problem, then watch the agent get smarter. Memory is the star.

## Setup (before judges arrive)
```bash
python run.py          # auto-seeds 8 historical incidents, serves http://127.0.0.1:8000
```
Have the browser open on the console. Optionally set `GROQ_API_KEY` for live LLM reasoning.

## Beat 1 — The pain (10s)
> "It's a flash sale. checkout-service just started throwing 503s. Our on-call engineer has
> never seen this exact alert. Normally they'd spend 30 minutes digging through old postmortems."

## Beat 2 — Without memory (15s)
Run the terminal showcase in a second pane:
```bash
python -m incident_commander.cli demo
```
Point at **Interaction #1 (empty memory)**: the agent gives *generic* advice. "No prior memory
matched — this looks novel." This is every stateless chatbot.

## Beat 3 — With memory, the reveal (30s)
Point at **the same incident with seeded memory**. The Memory panel lights up:
- Recalls **INC-2064** (checkout, same HikariCP timeout) and **INC-2041** (payments, same
  root cause) with relevance scores.
- The agent leads with the fix that *actually worked*: kill idle-in-transaction backends, then
  roll out PgBouncer — and notes it resolved in ~5 minutes last time.

> "Same model, same prompt. The only difference is memory. It just briefed the engineer in two
> seconds with the exact fix from six weeks ago."

## Beat 4 — The learning loop (20s)
In the web console, fill the **"Resolved? Teach the agent"** form and click *Retain postmortem*.
Watch the memory counter increment. 
> "Every incident makes it sharper. Day one it's generic. By incident #20 it's your best SRE
> who never forgets and never sleeps."

## Beat 5 — Reflect / trends (15s)
In the Memory panel, ask: *"what keeps breaking payments-api?"* → the agent synthesizes an
observation across incidents (connection-pool exhaustion recurs under traffic spikes).
> "It doesn't just recall — it consolidates patterns. That's Hindsight's reflect step."

## Closing line
> "Incident Commander turns tribal incident knowledge into an institutional memory that
> compounds. That's a product PagerDuty and incident.io customers would pay for today."

## Talking points if asked
- **Why Hindsight?** Temporal + entity-graph retrieval beats naive vector search — "what broke
  payments in July" needs time reasoning, not just similarity.
- **Edge cases handled:** empty memory (novel incident), Groq function-calling/rate-limit errors
  (retry + fallback), SDK version drift (defensive response normalization).
- **Path to adoption:** ingest real postmortems from Jira/PagerDuty; wire alerts straight to
  `recall()`.
