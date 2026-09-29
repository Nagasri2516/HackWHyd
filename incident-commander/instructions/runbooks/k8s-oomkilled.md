# Runbook: Kubernetes OOMKilled Pods

**Applies to:** any containerized service on the cluster
**Signature:** `Reason: OOMKilled`, `exit code 137`, pods CrashLoopBackOff after a deploy

## Symptoms
- Pods restart repeatedly; `kubectl get pods` shows high `RESTARTS`.
- `kubectl describe pod <pod>` → `Last State: Terminated, Reason: OOMKilled`.
- Memory usage sawtooths up to the limit then drops on restart.

## Immediate mitigation
1. Confirm the cause:
   `kubectl describe pod <pod> | grep -A5 "Last State"`
2. Check limits vs usage:
   `kubectl top pod <pod>`
3. If a recent deploy shipped a memory regression, **roll back**:
   `kubectl rollout undo deployment/<name>`
4. As a stopgap, raise the memory limit and add replicas to spread load.

## Durable fix
- Profile for leaks (heap dump / pprof). Fix the actual growth.
- Set `requests`/`limits` from real p99 memory + headroom (~30%).
- Add an HPA on memory if load is spiky.

## Verification
- Zero OOMKills for 30 minutes.
- `kubectl top pod` shows steady memory below the limit.
