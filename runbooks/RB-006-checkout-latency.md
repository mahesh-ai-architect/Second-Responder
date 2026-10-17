# RB-006: Checkout latency regression after deploy

**Service:** checkout | **Owner:** growth team | **Typical severity:** SEV2 if conversion impact confirmed

## Symptoms
- Checkout p99 latency above 2.5s against a 900ms baseline
- APM traces show time concentrated in promo validation or the inventory call

## First checks
1. APM waterfall for a slow trace: which span eats the time?
2. Was "checkout_v2" enabled in the last deploy?
3. Check for N+1 query patterns in cart service database calls.

## Diagnosis
- Promo validation called synchronously per cart item: known regression pattern from the v2 flag.
- Cache bypass header set by the new frontend build: every request hits origin services.
- DB time dominant: hand off to RB-009.

## Remediation
1. Disable the flag: `checkout_v2=false` - instant rollback, no deploy needed.
2. Enable async promo validation: `promo.async_validation=true`
3. Verify p99 below 1.2s for 10 minutes before closing.

## Escalation
Growth team lead. SEV2 if analytics confirms a conversion drop.
