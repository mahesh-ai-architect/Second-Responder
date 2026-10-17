# RB-003: SSO login failure spike

**Service:** auth-service | **Owner:** identity team | **Typical severity:** SEV1 if all SSO logins fail

## Symptoms
- Login success rate below 90%
- Errors: "SAML signature validation failed" and "OIDC discovery document fetch failed"

## First checks
1. Fetch the IdP discovery document: `curl https://idp.example.com/.well-known/openid-configuration`
2. Compare the IdP signing certificate fingerprint against the configured metadata.
3. Check node clock drift: `chronyc tracking` - drift above 30 seconds breaks token validation.

## Diagnosis
- Most common cause: the IdP rotated its signing certificate and our cached metadata is stale.
- Discovery fetch failing: IdP outage or a network/DNS change on our side.
- Signature failures plus clock drift: fix NTP before touching metadata.

## Remediation
1. Refresh IdP metadata from the admin console: Identity Providers -> Reload metadata.
2. Clear cached keys: `kubectl rollout restart deploy/auth-service -n prod`
3. If the IdP is down, post the status page notice and wait - do not bypass signature checks.

## Escalation
SEV1 if all SSO logins are failing (workforce lockout). Page the identity on-call lead immediately.
