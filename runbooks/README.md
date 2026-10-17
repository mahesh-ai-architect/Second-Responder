# Week 2 RAG corpus - runbooks

12 markdown runbooks covering the same 8 services as the Week 1 incident dataset:
payments-api (RB-001, RB-002), auth-service (RB-003, RB-004), search (RB-005),
checkout (RB-006), notifications (RB-007), database-primary (RB-008, RB-009),
cdn-edge (RB-010), inventory (RB-011), plus RB-012, a severity and escalation
guide that applies across all services (good for multi-document questions).

Each runbook has consistent sections (Symptoms, First checks, Diagnosis,
Remediation, Escalation) and contains exact strings worth testing hybrid
retrieval against: error messages, queue names, feature flags, commands.
Synthetic data - safe to publish on GitHub.
