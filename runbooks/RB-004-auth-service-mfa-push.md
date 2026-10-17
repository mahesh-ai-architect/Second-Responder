# RB-004: MFA push delivery degraded

**Service:** auth-service | **Owner:** identity team | **Typical severity:** SEV3 (SEV2 if >30 minutes)

## Symptoms
- Push approval latency above 60 seconds, or failures with "push token revoked"
- Users report not receiving MFA prompts

## First checks
1. Check the push vendor status page (APNs/FCM relay provider).
2. Token revocation rate split by platform: iOS vs Android.
3. Confirm TOTP (authenticator app) logins are unaffected.

## Diagnosis
- One platform only: platform gateway or vendor-side issue.
- Both platforms: our notification service or vendor account throttling.

## Remediation
1. Advise users to fall back to authenticator app (TOTP) codes - use the comms template in the incident channel.
2. If single-platform, open a vendor ticket with sample device tokens and timestamps.
3. Never disable or weaken MFA to "fix" delivery problems.

## Escalation
Identity lead plus a vendor P1 ticket if degradation lasts more than 30 minutes or blocks a SEV1/SEV2 response.
