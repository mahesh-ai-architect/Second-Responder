# RB-011: Stock sync failures and oversell alerts

**Service:** inventory | **Owner:** growth team | **Typical severity:** SEV2 while oversell is active

## Symptoms
- Stock sync job failing; oversell alerts on high-velocity SKUs
- Errors: "deadlock detected on sku_locks", or the feed file is missing the column "warehouse_id"

## First checks
1. Is more than one sync run executing at once? Overlapping runs deadlock each other.
2. Diff the latest warehouse feed file against the expected schema.
3. Check whether the batch repricing job is running concurrently.

## Diagnosis
- Missing "warehouse_id" column: the warehouse changed the feed schema without notice.
- Deadlocks with overlapping runs: scheduling collision, not bad data.
- Deadlocks with repricing: lock ordering conflict between the two jobs.

## Remediation
1. Stop extra sync runs; rerun a single sync in idempotent reconcile mode: `stock-sync --mode=reconcile`
2. Reconcile counts for affected SKUs from the latest warehouse snapshot.
3. For oversold orders, follow the customer outreach macro - do not hand-edit stock counts outside reconcile mode.

## Escalation
SEV2 while oversell is active (customer-facing). Notify growth and support leads.
