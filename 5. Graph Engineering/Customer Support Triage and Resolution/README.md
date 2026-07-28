# Customer Support Triage & Resolution

**Layer**: Graph Engineering (July 2026)

## Goal
Tickets arrive → triage by complexity → route to right agent (FAQ, specialist, human) → resolve & track.

## Graph Structure
```
NODES:
  1. IntakeAgent: Reads ticket, classifies urgency/complexity
  2. FAQAgent: Tries to answer from docs
  3. SpecialistAgent (Billing): Handles billing issues
  4. SpecialistAgent (Technical): Handles tech issues
  5. SpecialistAgent (Product): Handles feature/usage questions
  6. EscalationAgent: Prepares case for human if needed
  7. FeedbackAgent: Learns from resolution, improves FAQ

EDGES:
  Ticket → IntakeAgent (classify)
             ├─→ Simple FAQ → FAQAgent (loop: try answer, verify satisfaction)
             │                   ├─→ Resolved → FeedbackAgent → Close
             │                   └─→ Unresolved → EscalationAgent → Human
             │
             ├─→ Billing → BillingSpecialist (loop: analyze, resolve)
             │                ├─→ Resolved → FeedbackAgent → Close
             │                └─→ Escalate → EscalationAgent → Human
             │
             ├─→ Technical → TechSpecialist (loop: diagnose, fix)
             │                ├─→ Resolved → FeedbackAgent → Close
             │                └─→ Escalate → EscalationAgent → Human
             │
             └─→ Product → ProductSpecialist
                            ├─→ Resolved → FeedbackAgent → Close
                            └─→ Escalate → EscalationAgent → Human
```

## Each Agent's Loop

**IntakeAgent**
- Observe: Raw ticket text
- Decide: Urgency? Complexity? Category?
- Act: Classify, route
- Verify: Classification confidence > 80%?

**FAQAgent**
- Observe: Customer question
- Decide: Does FAQ contain answer?
- Act: Retrieve relevant docs, compose response
- Verify: Response directly answers question?
- Loop: If answer doesn't satisfy (customer says "this doesn't help"), escalate

**SpecialistAgent** (e.g., Billing)
- Observe: Billing issue
- Decide: What kind? (invoice dispute, pricing question, subscription issue?)
- Act: Investigate (pull invoice, check agreement, run calculations)
- Verify: Do findings explain customer's confusion?
- Loop: If not, gather more data, try again

**EscalationAgent**
- Observe: Ticket + failed resolution attempts
- Decide: Why did it fail? What info would human need?
- Act: Summarize ticket, list failed attempts, flag urgency
- Verify: Summary is clear? Human can pick it up?

## State Across Edges
- Ticket metadata (shared with all agents)
- Customer history (pull up past tickets, preferences)
- Knowledge base (FAQ, policies)
- Resolution (from any specialist → FeedbackAgent → Close)

## When to Use This Layer
- Multiple agents with different expertise
- Workflow requires handoffs (agent A → agent B → agent C)
- Verification chains (each agent checks previous agent's work)
- Multi-step pipelines (data → analysis → decision → action)
- Enterprise-scale (needs audit trails, compliance, observability)
