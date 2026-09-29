# Runbook: Bad Deploy / Rollout Regression

**Applies to:** any service behind CI/CD
**Signature:** error rate or latency steps up **immediately after a deploy**; the graph has
a clean "before/after" edge aligned to a release timestamp.

## Symptoms
- 5xx / exception rate jumps within minutes of a rollout.
- The change is isolated to one service/version; healthy replicas run the old version.
- No infra event (node, network, DB) correlates — only the release does.

## Immediate mitigation
1. Correlate the spike start with the deploy timeline (release annotations).
2. Roll back first, diagnose second:
   `kubectl rollout undo deployment/<name>` or re-point the traffic to the previous version.
3. Freeze the pipeline for that service until root cause is understood.

## Durable fix
- Require canary / progressive delivery with automatic rollback on SLO breach.
- Add the failing scenario to the pre-merge test suite.
- Gate deploys on golden-signal health checks.

## Verification
- Error rate returns to baseline immediately after rollback (strong confirmation the deploy
  was the cause).
