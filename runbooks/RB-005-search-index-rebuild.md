# RB-005: Search index rebuild stalled

**Service:** search | **Owner:** platform team | **Typical severity:** SEV3 (SEV2 if customer-facing results stale > 2 hours)

## Symptoms
- Nightly job "indexer-nightly" stuck, shard progress frozen
- Error "mapper_parsing_exception" in indexer logs, or a data node above 85% disk

## First checks
1. Disk usage per data node; indexing halts at the high watermark.
2. Indexer logs for "mapper_parsing_exception" - a field arrived with a conflicting type.
3. GC pause times on data nodes.

## Diagnosis
- Disk above watermark: snapshots or old indices consuming space.
- Mapping exception: a producer started sending a field with a new type.
- Progress frozen with healthy disk: long GC or a hung shard task.

## Remediation
1. Delete snapshots beyond retention; delete closed indices older than 90 days.
2. Fix the mapping for the offending field, or route that field to a quarantine index.
3. Resume the job from its checkpoint: `indexer-nightly --resume-from-shard`
4. If users also report worse results, check the last search deploy for analyzer changes before blaming the index.

## Escalation
Platform on-call lead if customer-facing search results are stale for more than 2 hours.
