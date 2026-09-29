# How this project maps to the judging criteria

| Criteria | Weight | How Incident Commander scores |
|---|---|---|
| **Innovation** | 30% | Not a chatbot — an SRE agent that turns tribal incident knowledge into compounding institutional memory. It leads with *the fix that worked last time*, cites incident IDs, and consolidates trends. A genuinely fresh take on the incident-response space (PagerDuty / incident.io / FireHydrant). |
| **Use of Hindsight Memory** | 25% | Memory is the entire value proposition, not a feature. `retain` (postmortems as world + experience facts), `recall` (grounds every diagnosis), `reflect` (trend synthesis). The UI's centerpiece is a live Memory panel. We show a hard **before/after**: identical model + prompt, memory off vs on. |
| **Technical Implementation** | 20% | Clean layered architecture, one `MemoryStore` interface with two backends, Markdown-defined behavior, retries + graceful degradation for Groq, defensive SDK normalization, 5 passing tests, runs offline with zero config. |
| **User Experience** | 15% | 90-second demo story that lands in one glance. Polished ops-console UI where recalled memories animate in with scores; one-click seed, example, diagnose, and teach-the-agent flows. CLI for terminal-native SREs. |
| **Real-world Impact** | 10% | MTTR is a line item every engineering org tracks. Clear adoption path: ingest real postmortems from Jira/PagerDuty, wire alerts to `recall()`. Would plausibly sell at $50+/seat/month. |

## The one thing to remember
> **Same LLM. Same prompt. Memory off = generic. Memory on = expert.**
> That single comparison is the whole pitch, and it's exactly what the 25% memory criterion
> rewards.

## Evidence to show judges
- `python -m incident_commander.cli demo` — the before/after in the terminal.
- The web Memory panel recalling INC-2064 / INC-2041 with relevance scores.
- `data/incidents.json` — 8 realistic postmortems (the data is what makes it look real).
- `pytest -q` — green, including a test that proves recall is empty *before* a resolve and
  populated *after* (the learning loop, asserted).
