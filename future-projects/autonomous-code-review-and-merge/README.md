# Autonomous Code Review and Merge

**Layer**: Loop Engineering (2026)

## Goal
PR arrives → agent reads code → writes tests if missing → runs full suite → checks coverage → suggests improvements → auto-merges if everything passes.

## Loop Structure
```
OBSERVE:
  - Read PR description
  - Fetch changed files
  - Read existing tests
  - Check test coverage baseline
PLAN:
  - What's the risk level? (small fix vs core logic change)
  - What tests are missing?
  - What edge cases might break?
ACT:
  - Write tests for new functionality
  - Write tests for edge cases
  - If needed, suggest code improvements (but don't change submitted code)
VERIFY:
  - Run test suite (unit + integration)
  - Check coverage improvement (must be >= current baseline)
  - Lint and style checks
  - Security scan
DECIDE:
  - All checks pass + coverage OK? Approve & merge.
  - Some tests fail? Explain failure, suggest fix, loop back to ACT.
  - Coverage dropped? Reject, explain, request human intervention.
  - Tried 5 times, still failing? Escalate to human.
```

## Verifier as Bottleneck
The test suite is the ground truth, not the agent's reasoning. If tests pass, it's good. If they fail, the agent learns that and adjusts.

## Real Example
SWE-agent research showed that interface quality (how the agent reads/writes files) had 3.54x impact on success rate vs raw model capability.

## When to Use This Layer
- Tasks lasting minutes to hours
- Verification is possible (tests, schemas, external feedback)
- Iteration improves quality
- Single agent doing complex work
- The task has a clear stopping condition ("tests pass", "schema valid", "performance target met")

## Build Plan

**MVP**: On a sample PR: analyze diff → add missing tests → run suite → approve/merge or escalate after N failures.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Observe/plan | PR fetch, risk classification, missing-test detection |
| 2. Act | Write tests; suggest (don’t rewrite) author code |
| 3. Verify bottleneck | Tests/lint/coverage as ground truth |
| 4. Stop conditions | Merge if green; escalate after 5 failed loops |

**Done when**: Agent merges only when suite passes + coverage ≥ baseline; failures produce actionable comments.
**Estimate**: 2.5 weeks · **Target finish**: Jan 2, 2027
