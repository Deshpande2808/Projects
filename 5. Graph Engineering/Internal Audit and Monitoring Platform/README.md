# Internal Audit & Monitoring Platform

**Layer**: Graph Engineering (July 2026)

## Goal
Monitor infrastructure health, detect anomalies, investigate, remediate, and audit.

## Graph Structure
```
NODES:
  1. QueryAgent: Answers questions about infrastructure
  2. AnomalyAgent: Monitors metrics, flags deviations
  3. InvestigationAgent: Deep-dives into flagged anomalies
  4. RemediationAgent: Proposes & executes fixes
  5. PolicyAgent: Checks all actions against compliance rules
  6. EscalationAgent: Prepares critical issues for human

EDGES:
  Continuous:
  MetricsStream → AnomalyAgent (loop: detect deviations)
                    ├─→ Normal → Continue monitoring
                    └─→ ANOMALY → InvestigationAgent
                                    ↓
                                  PolicyAgent (parallel check)
                                    ├─→ APPROVED → RemediationAgent (try fix)
                                    │              ├─→ Fixed → Monitor
                                    │              └─→ Failed → EscalationAgent → Human
                                    └─→ BLOCKED → EscalationAgent → Human

  On-demand:
  UserQuery → QueryAgent (answer infrastructure questions)
```

## Each Agent's Loop

**AnomalyAgent**
- Observe: Incoming metrics (CPU, memory, request latency, error rate)
- Decide: Is this outside normal range? Use baseline + seasonal patterns
- Act: Flag as anomaly if deviation > threshold
- Verify: Is flag real or noise?

**InvestigationAgent**
- Observe: Flagged metric + recent events (deployments, traffic spikes)
- Decide: What's the likely cause? (code change, traffic surge, hardware issue, external API?)
- Act: Gather more data (logs, traces, related metrics)
- Verify: Does investigation narrative explain the anomaly?
- Loop: If unexplained, dig deeper

**RemediationAgent**
- Observe: Root cause identified
- Decide: What action fixes it? (restart service, scale up, rollback, etc)
- Act: Execute fix (with safeguards)
- Verify: Did fix resolve anomaly? Recheck metrics.
- Loop: If not fixed, try alternate remedy

**PolicyAgent**
- Observe: Proposed remedy from RemediationAgent
- Decide: Is this action compliant? (maintenance window allowed? Rollback safe? Approval needed?)
- Act: Check against policies
- Verify: Pass/fail
- If blocked: Escalate instead of letting remediation proceed

## When to Use This Layer
- Multiple agents with different expertise
- Workflow requires handoffs (agent A → agent B → agent C)
- Verification chains (each agent checks previous agent's work)
- Multi-step pipelines (data → analysis → decision → action)
- Enterprise-scale (needs audit trails, compliance, observability)
