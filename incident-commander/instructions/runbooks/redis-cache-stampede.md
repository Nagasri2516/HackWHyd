# Runbook: Redis Cache Stampede / Latency Spike

**Applies to:** services using Redis for caching (checkout-service, catalog-api)
**Signature:** `LOADING Redis is loading the dataset in memory`, timeouts to Redis,
p99 latency spike right after a cache flush or restart.

## Symptoms
- Latency spikes correlate with cache miss rate jumping to ~100%.
- Database load spikes at the same moment (traffic that cache normally absorbs).
- Redis CPU or network saturated; `INFO stats` shows `keyspace_misses` climbing.

## Immediate mitigation
1. Confirm miss storm: `redis-cli INFO stats | grep keyspace`
2. Check evictions/memory: `redis-cli INFO memory | grep -E "used_memory_human|maxmemory"`
3. If DB is melting, enable request coalescing / rate-limit cache rebuilds.
4. Warm hot keys manually if a known set drives most traffic.

## Durable fix
- Add jittered TTLs so keys don't all expire together.
- Use a single-flight / lock so only one worker rebuilds a hot key.
- Set `maxmemory-policy allkeys-lru` and size memory for the working set.

## Verification
- Cache hit rate returns above ~90%.
- DB load and p99 latency return to baseline.
