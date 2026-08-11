# GCP Infrastructure Provisioner

**Layer**: Harness Engineering (2026)

## Goal
Developers request infrastructure (new service, database, load balancer). Agent provisions it safely, following company standards.

## Harness Components

### Tools (Carefully scoped)
- Create GCP resources (compute, storage, networking)
- Describe resources (read-only)
- NO permissions to delete, downscale, or modify existing resources
- Audit logs (read permissions to see what others deployed)
- Approval workflow (submit for human review)

### Guardrails (Safety-critical)
- Enforce security group policies (no "0.0.0.0")
- Enforce naming conventions (prod-*, staging-*, dev-*)
- Enforce quota limits (no resource spinning up more than Y instances)
- Enforce cost controls (flag if new resource exceeds $Z/month)
- Require tags (so costs are tracked by team/project)
- Require approval if change impacts production

### Verification Loop
- Observe: Deployment request + requirements
- Decide: What resources needed? Which region? What configuration?
- Act: Generate Terraform/IaC, submit for dry-run
- Verify: Dry-run succeeds? Cost estimate reasonable? Naming/security correct?
- Human approves OR rejects with feedback
- If approved: execute; if rejected: modify and re-submit

### Context & Memory
- Company standards (security policies, tagging scheme, regions approved)
- Existing infrastructure graph (to avoid duplication)
- Resource templates (for common deployment patterns)
- Cost baseline (to detect runaway spending)

### Observability
- Trace: Every deployment decision (why did you choose this machine type?)
- Audit: All infrastructure changes (Git-like history)
- Metrics: Deployment success rate, approval rate, cost accuracy
- Rollback: Can revert to previous infrastructure state

## Success Criteria
- 100% compliance with company security/naming policies
- Zero production outages from misconfigured resources
- Faster provisioning than manual (minutes vs hours)
- Cost estimates within 10% of actual

## When to Use This Layer
- Multi-hour or multi-day agent runs
- Autonomous execution (agent runs while you sleep)
- Production systems (must be reliable)
- Safety-critical decisions (trading, infrastructure, customer data)
- Compliance requirements (audit trails, approval gates)

## Build Plan

**MVP**: Request → Terraform/IaC plan → policy checks + cost estimate → human approve → apply (create-only tools).

| Milestone | Deliverable |
|-----------|-------------|
| 1. Scoped tools | Create/describe only; no delete/downscale |
| 2. Policy engine | Naming, tags, no open SG, quotas, cost flags |
| 3. Dry-run loop | Plan → verify → revise → approve |
| 4. Audit trail | Full decision + apply history |

**Done when**: Policy violations always blocked; dry-run required before apply; cost estimate within ±10% on sample plans.
**Estimate**: 2.5 weeks · **Target finish**: Dec 16, 2026
