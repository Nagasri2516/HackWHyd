# I gave an AI on-call engineer a memory — and it stopped re-solving the same outages

*Building Incident Commander with Hindsight and Groq*

## The 2am problem
Every engineer who has been on-call knows the feeling: an alert fires, production is degraded,
and somewhere deep down you *know* the team has seen this before. But the fix lives in a Slack
thread from four months ago, a half-written postmortem, and one senior engineer's head — and
they're asleep. So you rediscover the answer from scratch while the revenue meter runs.

Incident knowledge is one of the most valuable assets an engineering org has, and it's almost
always trapped in people and forgotten docs. I wanted to fix that with an agent that never
forgets an incident.

## Why memory changes everything
Most "AI SRE" demos are a chatbot wrapped around an LLM. Ask it about a connection-pool timeout
and it gives you a textbook answer — the same one it would give any company on earth. Useful
once, forgettable forever.

The moment you add **memory**, the agent stops being generic. It stops answering *"what usually
causes this?"* and starts answering *"what caused this **for us**, and what did **we** do about
it?"* That's the difference between advice and a fix.

## How it works
Incident Commander is built on two pieces of tech:

- **[Hindsight](https://hindsight.vectorize.io/)** — an agent-memory layer with three
  operations: `retain`, `recall`, and `reflect`.
- **[Groq](https://groq.com/)** — a blazing-fast LLM endpoint (I used `openai/gpt-oss-120b`).

The loop is simple and it compounds:

1. **Recall.** A new incident arrives. The agent calls `recall()` with the service and error
   signature. Hindsight runs keyword, vector, full-text, entity-graph, and temporal search in
   parallel and returns the most similar past incidents.
2. **Reason.** Those past incidents — plus the matching runbook — are fed to Groq, which writes a
   structured response: assessment, most-likely root cause with a confidence score, immediate
   copy-pasteable actions, and the memory it relied on.
3. **Retain.** When the incident is resolved, the agent writes the postmortem back into
   memory as a *world fact* (what happened) and an *experience fact* (what worked).

Interaction #1 is generic. By interaction #20, it's your most senior SRE who never sleeps.

## The demo that makes people lean in
I run the *exact same incident* twice — a checkout-service 503 storm during a flash sale —
with the *same model and same prompt*. The only variable is memory.

- **Memory off:** "This looks novel. Check your golden signals…" Generic.
- **Memory on:** "This matches INC-2064 and INC-2041 — connection-pool exhaustion under a traffic
  spike. Kill idle-in-transaction backends now, then roll out PgBouncer. That fixed it in about
  five minutes last time."

Same brain. Memory is the whole difference. That's exactly what makes memory-powered agents
exciting — and why Hindsight is 25% of this hackathon's score.

## What I learned
- **The data is the product.** I spent as much time crafting realistic postmortems (real error
  signatures, real commands, real root causes) as I did on code. Believable memory is what sells
  the demo.
- **Handle LLM errors like production.** Groq is fast, but function-calling and rate-limit errors
  happen — retries plus a graceful fallback kept the agent always-on.
- **Make memory visible.** The UI's centerpiece is a live Memory panel that animates in the
  recalled incidents with relevance scores. If memory is the value, show it.

## Where this goes
Wire it to real postmortems in Jira or PagerDuty, point your alerting straight at `recall()`, and
you have an institutional memory that lowers MTTR every single week. Tribal knowledge becomes a
compounding asset instead of a bus-factor risk.

The best hackathon projects are the ones you'd actually use. I'd deploy this one.

*Code: [GitHub repo link] · Built with Hindsight + Groq.*
