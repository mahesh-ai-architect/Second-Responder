# RB-008: Database replication lag on primary

**Service:** database-primary | **Owner:** platform (DB) team | **Typical severity:** SEV2 (SEV1 if lag > 300s with unhealthy primary)

## Symptoms
- Replica lag above 30 seconds and climbing in pg_stat_replication
- Read-your-write complaints from application teams

## First checks
1. `SELECT pid, application_name, now() - xact_start AS xact_age FROM pg_stat_activity ORDER BY xact_age DESC;`
2. Identify bulk jobs by application_name - backfills are the usual blocker.
3. Replica disk I/O utilisation.

## Diagnosis
- One long transaction on the primary: replica replay is blocked behind it.
- Backfill job running during peak: contention, not failure.
- Replica disk saturated: replay cannot keep up even with a healthy primary.

## Remediation
1. With incident commander approval, terminate the blocking backfill: `SELECT pg_terminate_backend(<pid>);`
2. Throttle or pause batch jobs until lag drains below 5 seconds.
3. Controlled failover only if the primary is genuinely failing AND lag is under 10 seconds.
4. Never promote a replica with lag above 300 seconds without data-loss sign-off from the DB lead.

## Escalation
SEV1 if lag exceeds 300 seconds with an unhealthy primary. Page the DB lead.
