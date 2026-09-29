# Runbook: Database Connection Pool Exhaustion

**Applies to:** any service backed by PostgreSQL (payments-api, checkout-service, orders-api)
**Signature:** `FATAL: remaining connection slots are reserved` / `timeout acquiring connection`
/ HikariCP `Connection is not available, request timed out after 30000ms`

## Symptoms
- Sudden spike in 5xx / 500 errors on write-heavy endpoints.
- Request p99 latency climbs while CPU stays moderate.
- DB `pg_stat_activity` shows connections at or near `max_connections`.

## Immediate mitigation
1. Check active connections:
   `SELECT count(*) FROM pg_stat_activity;`
2. Identify hogs (idle-in-transaction):
   `SELECT pid, state, query_start, query FROM pg_stat_activity WHERE state = 'idle in transaction' ORDER BY query_start;`
3. Terminate long idle-in-transaction sessions:
   `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle in transaction' AND now()-query_start > interval '5 minutes';`
4. If a recent deploy raised pool size beyond DB capacity, **roll it back**.

## Durable fix
- Right-size the pool: `pool_size <= max_connections / replicas`.
- Add PgBouncer (transaction pooling) in front of Postgres.
- Ensure transactions are short; never hold a connection across an external HTTP call.

## Verification
- 5xx rate returns to baseline within 5 minutes.
- `pg_stat_activity` count stabilizes well below `max_connections`.
