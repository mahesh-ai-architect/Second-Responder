# RB-010: CDN cache hit ratio drop and edge 503s

**Service:** cdn-edge | **Owner:** platform team | **Typical severity:** SEV2 if origin is saturating

## Symptoms
- Cache hit ratio below 70% against a 92% baseline
- Origin traffic roughly 3x normal; scattered 503s by POP after a config push

## First checks
1. Hit ratio split by POP and by path - global or localized?
2. Was there a CDN config push or a full purge in the last hour?
3. Origin response codes and origin CPU.

## Diagnosis
- Cache key changed to include the session cookie: every user becomes a unique cache entry.
- Full purge during peak: self-inflicted origin stampede.
- One POP only: bad config version on that POP or an origin shield misroute.

## Remediation
1. Roll back the CDN config to the previous known-good version.
2. Enable origin shield and request coalescing to protect the origin.
3. Re-warm the top 500 URLs after rollback.
4. Disable scheduled purges until the root cause is confirmed.

## Escalation
SEV2 if the origin is saturating. Protect the origin first, investigate second.
