# Triage Playbook

Use this playbook to classify and prioritize an incoming incident before diagnosing.

## Severity ladder
- **SEV1** — Full outage or data loss. Customer-facing, revenue-impacting. Page everyone.
- **SEV2** — Major degradation. Core feature broken for many users. Elevated error rate.
- **SEV3** — Partial/edge degradation. Workaround exists. Single non-critical service.
- **SEV4** — Cosmetic or internal-only. No customer impact.

## Signals to extract from the report
- **Blast radius**: how many services / users / regions?
- **Error signature**: exact error string, HTTP status, exit code, stack trace.
- **Trend**: is it getting worse, flat, or recovering?
- **Recent change**: any deploy, config change, or infra event in the last 60 minutes?
- **Saturation**: CPU, memory, connection pool, disk, queue depth near limits?

## Golden signals to always check
1. **Latency** — p50 / p95 / p99 request duration.
2. **Traffic** — requests per second vs. baseline.
3. **Errors** — 5xx rate, exception rate, retry storms.
4. **Saturation** — the most constrained resource (pool, memory, CPU, disk).

## Bias toward memory
Before reasoning from scratch, check whether the error signature or symptom matches a
**recalled past incident**. Teams repeat the same failure modes. The fastest path to
resolution is usually the one that worked last time.
