# Social media posts

## LinkedIn (long form)
🚨 What if your on-call engineer never forgot an outage?

This weekend I built **Incident Commander** — an AI SRE agent that *remembers every incident*
your team has ever resolved, and uses that memory to fix the next one in minutes.

The magic isn't the LLM. It's the memory.

I ran the SAME incident twice — same model, same prompt — a checkout 503 storm during a flash
sale:

❌ Without memory: "This looks novel, check your golden signals…" (generic advice)
✅ With memory: "This matches INC-2064 & INC-2041 — connection-pool exhaustion under a traffic
spike. Kill idle-in-transaction backends, then roll out PgBouncer. Fixed it in ~5 min last time."

Built with:
🧠 Hindsight (@Vectorize) for agent memory — retain / recall / reflect
⚡ Groq for a fast LLM (openai/gpt-oss-120b)

Every resolved incident gets written back into memory, so the agent gets sharper over time.
Day one it's generic. By incident #20 it's your most senior SRE who never sleeps.

Tribal incident knowledge → compounding institutional memory. That's a real MTTR lever.

#AI #AIagents #DevOps #SRE #Hindsight #Groq #buildinpublic

---

## X / Twitter (thread)
1/ I built an AI on-call engineer that never forgets an outage. 🚨🧠

Same LLM. Same prompt. The only difference is memory — and it's everything. 🧵

2/ Without memory, an "AI SRE" gives textbook advice any company would get.

With memory, it says: "This matches INC-2064 — connection-pool exhaustion. Kill idle-in-tx
backends, roll out PgBouncer. Fixed it in 5 min last time." That's a fix, not advice.

3/ Built on @vectorize_io Hindsight (retain/recall/reflect) + @GroqInc for speed.

Resolve an incident → it's written back to memory → the next one is diagnosed faster. The agent
compounds.

4/ Tribal incident knowledge is trapped in Slack threads and people's heads. Hindsight turns it
into institutional memory that lowers MTTR every week.

Demo + code 👇 #AI #DevOps #SRE

---

## One-liner (for submission blurb)
Incident Commander: an AI SRE that remembers every outage and uses Hindsight memory to resolve
the next one in minutes — same LLM, memory off = generic, memory on = expert.
