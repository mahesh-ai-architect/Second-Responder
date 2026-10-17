# RB-009: Connection pool exhaustion

**Service:** database-primary | **Owner:** platform (DB) team | **Typical severity:** SEV2

## Symptoms
- Application errors: "FATAL: remaining connection slots are reserved for non-replication superuser connections"
- PgBouncer client wait queue growing

## First checks
1. `SELECT application_name, state, count(*) FROM pg_stat_activity GROUP BY 1, 2 ORDER BY 3 DESC;`
2. PgBouncer: `SHOW POOLS;` - look at cl_waiting.
3. Sessions stuck in "idle in transaction" point at a leaking deploy.

## Diagnosis
- One application_name dominating with idle-in-transaction sessions: connection leak in a recent deploy.
- All apps up evenly: genuine load growth or a batch job.
- Pooler queue up but DB sessions low: pool size misconfigured after a deploy.

## Remediation
1. Restart the pooler to clear leaked sessions: `systemctl restart pgbouncer`
2. Roll back the leaking deploy; the leak, not the pool size, is the bug.
3. Temporary pool_size increase of 25% is allowed only if DB CPU is below 60%.

## Escalation
DB lead if it recurs twice in 24 hours - that is a leak hunt, treat as SEV2.
