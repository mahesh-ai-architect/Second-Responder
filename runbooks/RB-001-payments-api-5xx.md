# RB-001: Elevated 5xx errors on the /charge endpoint

**Service:** payments-api | **Owner:** payments team | **Typical severity:** SEV2 (SEV1 if >50% of charges failing)

## Symptoms
- Alert: "payments-api 5xx rate above 5% for 5 minutes"
- Logs show "502 upstream prematurely closed connection" and "stripe request timeout after 3000ms"
- Checkout failures rise in proportion to the error rate

## First checks
1. `kubectl rollout status deploy/payments-api -n prod` and `kubectl get pods -n prod -l app=payments-api`
2. Was there a deploy in the last 30 minutes? Check the deploy feed first.
3. Check status.stripe.com for an active Stripe incident.
4. Look at the orders DB connection pool (see RB-009 if saturated).

## Diagnosis
- Errors started within 10 minutes of a deploy: assume bad release until proven otherwise.
- Only /charge failing and Stripe status degraded: downstream provider issue, not us.
- 503s with "no healthy upstream": connection pool or target pod problem.

## Remediation
1. Bad deploy: `kubectl rollout undo deploy/payments-api -n prod`
2. Stripe degraded: enable queued-charge mode (`payments.queue_mode=true`) so charges retry asynchronously instead of failing at checkout.
3. Pool saturation: follow RB-009.

## Escalation
Escalate to the payments on-call lead if the error rate is above 20% or not resolved within 15 minutes. Declare SEV1 if more than 50% of charges are failing.

## After resolution
Confirm the error rate stays below 0.5% for 15 minutes before closing the incident.
