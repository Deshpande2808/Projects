# AI Services Company Operations (For Your Startup)

**Layer**: Graph Engineering (July 2026)

## Goal
Automate company operations: client onboarding → scoping → architecture → implementation → deployment.

## Graph Structure
```
NODES:
  1. IntakeAgent: Onboards client, gathers requirements
  2. EstimationAgent: Scopes work, estimates time/cost
  3. ArchitectureAgent: Designs system, recommends stack
  4. ImplementationAgent: Builds (code, test, iterate)
  5. DeploymentAgent: Stages, deploys, monitors
  6. MonitoringAgent: Watches post-deployment
  7. ClientFeedbackAgent: Gathers feedback, logs learnings
  8. FinanceAgent: Tracks costs, profitability

EDGES:
  Client Inquiry
    ↓
  IntakeAgent (loop: gather complete requirements)
    ↓
  EstimationAgent (loop: estimate time/cost, validate with client)
    ├─→ Approved → ArchitectureAgent
    └─→ Too expensive → RenegotiateAgent (try cheaper approach)
    ↓
  ArchitectureAgent (loop: design, get client buy-in)
    ├─→ Approved → ImplementationAgent
    └─→ Concerns → Redesign (loop back)
    ↓
  ImplementationAgent (loop: build, test, iterate)
    ├─→ Complete → DeploymentAgent
    └─→ Blockers → EscalationAgent (human involved)
    ↓
  DeploymentAgent (loop: stage, verify, deploy to prod)
    ├─→ Successful → MonitoringAgent
    └─→ Issues → Rollback, troubleshoot, re-deploy
    ↓
  MonitoringAgent (loop: watch metrics, alert on errors)
    ├─→ Healthy → ClientFeedbackAgent
    └─→ Issue → AlertTeam
    ↓
  ClientFeedbackAgent (loop: gather feedback, improve process)
    ↓
  FinanceAgent (parallel: track project cost, actual vs estimate, profitability)
```

## State Across Edges
- Client requirements (Intake → Estimation → Architecture → Implementation)
- Architecture & tech stack (Architecture → Implementation → Deployment)
- Code (Implementation → Deployment → Monitoring)
- Costs (FinanceAgent monitors all phases)
- Performance metrics (Monitoring → ClientFeedback)

## When to Use This Layer
- Multiple agents with different expertise
- Workflow requires handoffs (agent A → agent B → agent C)
- Verification chains (each agent checks previous agent's work)
- Multi-step pipelines (data → analysis → decision → action)
- Enterprise-scale (needs audit trails, compliance, observability)

## Implementation Progression (from source doc)

### Phase 3: Introduce Graph (Month 3-4)
- Start simple: 2-3 agents coordinating
- Example: Data fetcher → Analyzer → Alert → Human review
- Learn handoff patterns: how agents communicate, what state they share
- Key learning: distributed-systems complexity (when does it help? when is it overhead?)

### Phase 4: Scale Graph (Month 4+)
- Internal operations (intake → estimation → architecture → build → deploy)
- At this stage, you'll have patterns and tools; orchestration becomes easier
