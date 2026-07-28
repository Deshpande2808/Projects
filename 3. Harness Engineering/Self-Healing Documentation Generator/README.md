# Self-Healing Documentation Generator

**Layer**: Harness Engineering (2026)

## Goal
Keep internal wiki/docs fresh by detecting stale sections and regenerating them from source code.

## Harness Components

### Tools
- Read source files (code)
- Diff versions (detect changes)
- Commit to wiki (write updates)
- Notify teams (via Slack/email)
- Rollback changes (if something goes wrong)

### Guardrails (Critical—docs are truth)
- Never delete—only append or suggest
- If generated text confidence < 80%, ask human
- Never overwrite manually-written sections without marking as AI-generated
- Preserve existing examples/explanations if they're good
- Require human review before publishing to main wiki

### Verification Loop
- Observe: Source code changed, fetch diff
- Decide: Does this impact the docs?
- Act: Generate updated doc section
- Verify: Is it accurate? Does it match code? Is prose clear? Are examples still valid?
- Iterate: Rewrite if unclear

### Context & Memory
- Cache of source file → doc section mappings
- History of changes (what was updated last month?)
- Ownership (which team maintains which docs?)
- Common patterns (how we document APIs, config, architecture)

### Observability
- Trace: Which code changes triggered doc updates
- Audit: All generated content (link to source + confidence score)
- Metrics: Staleness detection accuracy, user feedback on accuracy
- Feedback loop: Track which auto-generated docs got edited by humans (learn what you're getting wrong)

## Success Criteria
- Zero accidental deletions
- Docs stay within 2 weeks of code
- Confidence scores are calibrated (80% score = actually 80% human-acceptable)
- Teams trust the system enough to use it

## When to Use This Layer
- Multi-hour or multi-day agent runs
- Autonomous execution (agent runs while you sleep)
- Production systems (must be reliable)
- Safety-critical decisions (trading, infrastructure, customer data)
- Compliance requirements (audit trails, approval gates)
