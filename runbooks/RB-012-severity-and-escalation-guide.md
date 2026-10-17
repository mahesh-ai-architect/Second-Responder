# RB-012: Severity definitions and escalation guide

**Service:** all | **Owner:** infrastructure operations | **Applies to:** every incident

## Severity definitions and response targets
- **SEV1:** Customer-facing outage or data-loss risk. Acknowledge within 5 minutes. Incident commander required. Stakeholder updates every 30 minutes.
- **SEV2:** Major degradation of a customer-facing service. Acknowledge within 15 minutes. Updates hourly.
- **SEV3:** Minor degradation with a workaround available. Acknowledge within 60 minutes.
- **SEV4:** No customer impact. Acknowledge within 240 minutes; next business day is acceptable.

## Declaring and downgrading
- Any on-call engineer can declare a SEV1 or SEV2.
- Only the incident commander can downgrade a severity.
- When in doubt between two levels, declare the higher one - downgrading is cheap, under-declaring is not.

## Escalation chain
Service owner -> team on-call lead -> engineering manager -> director of infrastructure.
Page the next level if the current level has not engaged within the ack target for the severity.

## Communications and follow-up
- Status page updates are mandatory for SEV1 and SEV2.
- A blameless postmortem is required for every SEV1 and SEV2 within 3 business days, owned by the incident commander.
