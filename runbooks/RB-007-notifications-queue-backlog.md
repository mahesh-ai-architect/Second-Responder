# RB-007: Email and SMS queue backlog

**Service:** notifications | **Owner:** platform team | **Typical severity:** SEV3 (SEV2 if OTP/password-reset mail delayed > 15 min)

## Symptoms
- Email queue depth rising, send latency above 10 minutes
- Provider returns "429 provider rate limit exceeded"

## First checks
1. Split queue depth: transactional vs marketing. A campaign burst sharing the queue is the usual cause.
2. Worker replica count vs the autoscaling cap.
3. Provider rate limit status for our account.

## Diagnosis
- Marketing burst: a campaign send flooded the shared queue.
- Workers at cap with steady traffic: genuine capacity ceiling.
- 429s at low volume: provider-side throttling or account limit change.

## Remediation
1. Prioritize the "notifications-transactional" queue - OTP and password resets go first.
2. Raise worker replicas up to the max of 20.
3. Pause campaign sends: `campaigns.paused=true`
4. Never drop transactional messages to clear a backlog.

## Escalation
If password-reset or OTP mail is delayed more than 15 minutes this becomes auth-impacting - raise to SEV2 and cross-reference RB-004.
