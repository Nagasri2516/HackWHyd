# Demo video script (~2 minutes)

**Format:** screen recording with voiceover. Keep energy high; the reveal is at 0:45.

---

### 0:00–0:12 — Hook
*(Screen: the Incident Commander console, Memory panel visible on the right.)*

> "Every on-call engineer has re-solved an outage the team already fixed months ago. Tonight I'm
> going to give an AI agent a memory — and watch it fix the same incident 10x faster."

### 0:12–0:30 — The problem, set the scene
*(Type into the console: 'checkout-service 503s during a flash sale, HikariCP connection
timeouts, Postgres connections maxed'.)*

> "It's a flash sale. checkout-service is throwing 503s. This is a real, revenue-impacting
> incident. Let's see what a normal stateless agent does."

### 0:30–0:45 — Without memory (the baseline)
*(Run `python -m incident_commander.cli demo` in a terminal pane; point to Interaction #1.)*

> "With an empty memory, it's generic. 'This looks novel, check your golden signals.' Technically
> fine. Practically useless at 2am. This is every AI chatbot."

### 0:45–1:15 — The reveal: with memory
*(Point to the same incident WITH seeded memory. The Memory panel lights up.)*

> "Now the exact same incident — same model, same prompt — but the agent has memory. Watch the
> Memory panel. It instantly recalls INC-2064 and INC-2041 — the same connection-pool exhaustion,
> with relevance scores. And it leads with the fix that actually worked: kill idle-in-transaction
> backends, then roll out PgBouncer. It fixed this in five minutes last time."

> "That's Hindsight's `recall`. Memory is the only thing that changed — and it changed
> everything."

### 1:15–1:40 — The learning loop
*(In the web console, fill the 'Resolved? Teach the agent' form, click Retain. Counter ticks up.)*

> "Here's why it keeps getting better. When we resolve an incident, the agent writes the
> postmortem back to memory with Hindsight's `retain` — as a world fact and an experience fact.
> Day one it's generic. By incident #20 it's your most senior SRE who never sleeps."

### 1:40–1:55 — Reflect / trends
*(Ask in the Memory panel: 'what keeps breaking payments-api?')*

> "It doesn't just recall — with `reflect` it consolidates patterns across incidents into
> observations: connection-pool exhaustion keeps hitting payments-api under traffic spikes."

### 1:55–2:05 — Close
*(Zoom on the Memory panel / repo.)*

> "Incident Commander turns tribal knowledge into institutional memory that compounds and lowers
> MTTR. Built with Hindsight and Groq. Thanks for watching."

---

## Shot checklist
- [ ] Console open, memory seeded, browser clean (no dev tools).
- [ ] Terminal pane ready with `cli demo`.
- [ ] `GROQ_API_KEY` set for live LLM reasoning (optional but nicer).
- [ ] Memory panel visible the entire time — it's the star.
- [ ] Captions for the before/after lines.
