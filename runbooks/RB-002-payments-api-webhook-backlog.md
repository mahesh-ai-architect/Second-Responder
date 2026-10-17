# RB-002: Webhook delivery backlog

**Service:** payments-api | **Owner:** payments team | **Typical severity:** SEV3 (SEV2 if backlog > 50,000)

## Symptoms
- Queue "webhooks-inbound" depth above 10,000 and rising
- Consumer lag growing; downstream order and inventory states go stale
- Logs show "delivery attempt 8 failed, moving to DLQ"

## First checks
1. `kubectl get pods -n prod -l app=webhook-consumer` - look for CrashLoopBackOff
2. Check whether the same message_id is stuck at the head of the queue (poison message)
3. Check the downstream endpoint's own error rate

## Diagnosis
- Consumer crash-looping: usually a bad deploy or a config change.
- One message retried forever: poison message blocking the partition.
- Downstream endpoint returning 500s: fix the downstream service first, not the consumer.

## Remediation
1. Fix or roll back the consumer deploy.
2. Move the poison message to the DLQ manually, note its message_id in the incident timeline.
3. Scale consumers: `kubectl scale deploy/webhook-consumer -n prod --replicas=6`
4. Replay the DLQ only after the root cause is fixed. Webhook handlers are idempotent on event_id - verify the consumer checks event_id before replaying.

## Escalation
SEV2 if the backlog exceeds 50,000 or customer-visible order states are wrong.
