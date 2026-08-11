# Autonomous Bug Triage Agent

**Layer**: Harness Engineering (2026)

## Goal
Agent receives new bug tickets, triages them by severity/team, without human intervention (most of the time).

## Harness Components

### Tools
- Query Jira (read-only, search, fetch issue details)
- Run test suites (to understand scope of failure)
- Fetch logs from error tracking (understand impact)
- Comment on tickets (explain triage decision)
- Route to team Slack (notify responsible team)

### Guardrails (Preventive)
- Never close P0 or P1 tickets automatically
- Never assign to team without checking if they own that service
- Never comment without explaining the decision
- Block attempts to modify customer-facing data

### Verification Loop
- Observe: New bug arrives, read description + stack trace
- Decide: What's the severity? Which team owns it? Is it a duplicate?
- Act: Set priority, assign, comment with reasoning
- Verify: Does decision make sense? (check against: recent similar issues, team's current load, SLA impact)
- Correction: If uncertain, escalate instead of guessing

### Context & Memory
- Persistent: Which services each team owns (updated weekly)
- Session: Recent tickets (to catch duplicates)
- Knowledge: Common issues + resolutions for this service
- State: Current on-call engineer, team capacity

### Observability
- Trace: Every triage decision (why did you assign this to team X?)
- Audit: All assignments (who did what, when, why)
- Metrics: Triage accuracy rate, false escalations, time to triage
- Cost: Track API calls, avoid runaway inference

## Success Criteria
- Correct triage 95%+ of the time
- P0 bugs never auto-closed
- Human reviewers can audit decisions via traces
- Escalations are rare (1-2% of tickets)

## When to Use This Layer
- Multi-hour or multi-day agent runs
- Autonomous execution (agent runs while you sleep)
- Production systems (must be reliable)
- Safety-critical decisions (trading, infrastructure, customer data)
- Compliance requirements (audit trails, approval gates)

## Build Plan

**MVP**: New ticket → severity + team assignment + reasoned comment; escalate when uncertain. Mock Jira/Slack OK for v1.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Tool stubs | Issue fetch, search duplicates, comment, notify |
| 2. Guardrails | Never auto-close P0/P1; no assign without ownership map |
| 3. Triage loop | Observe → decide → act → verify → escalate |
| 4. Eval | Replay historical tickets; measure accuracy vs human labels |

**Done when**: ≥90% agreement with human triage on eval set; 100% of P0/P1 preserved; traces explain every assignment.
**Estimate**: 2 weeks · **Target finish**: Nov 15, 2026
