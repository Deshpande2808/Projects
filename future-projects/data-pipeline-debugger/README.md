# Data Pipeline Debugger

**Layer**: Loop Engineering (2026)

## Goal
Data pipeline fails silently. Agent observes failure → iterates through debugging → finds and fixes root cause.

## Loop Structure
```
OBSERVE:
  - Pipeline failed. Fetch error message.
  - Read logs (full stack trace)
  - Check data: What's the last successful checkpoint?
PLAN:
  - Where is the error likely? (Early, middle, or late in pipeline?)
  - What's the most probable cause? (Schema mismatch, missing data, API timeout?)
ACT:
  - Add targeted instrumentation (log at suspicious point)
  - Re-run pipeline
  - Check logs for new insights
VERIFY:
  - Did instrumentation help narrow down cause?
  - Is the error still at the same stage?
  - Does data at that checkpoint make sense?
LOOP:
  - If still unclear: Add more instrumentation, tighter scope
  - If clear: Generate fix (code change or configuration)
  - Re-run: Does fix resolve error?
  - Success: Deploy fix + remove debug instrumentation
  - Failure: Adjust hypothesis, try different cause, loop back to ACT
  - Max attempts: 6. If unsolved: Escalate with debug logs.
```

## Example
```
ERROR: CSV parser timeout on 50GB file upload
Attempt 1: Add logging to file size check → Finds file is 52GB, not 50GB
Attempt 2: Add logging to parser initialization → Parser tries to load entire file in memory
Attempt 3: Implement streaming parser → Succeeds
Fix: Switch to chunked streaming parser for files > 1GB. Re-run, success.
```

## When to Use This Layer
- Tasks lasting minutes to hours
- Verification is possible (tests, schemas, external feedback)
- Iteration improves quality
- Single agent doing complex work
- The task has a clear stopping condition ("tests pass", "schema valid", "performance target met")

## Build Plan

**MVP**: Inject failing pipeline jobs; agent instrument → re-run → hypothesize → fix → prove green within max attempts.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Sandbox pipeline | Small ETL with injectable failure modes |
| 2. Debug loop | Log → narrow → fix → re-run |
| 3. Instrumentation hygiene | Remove debug noise after success |
| 4. Cap + escalate | Max 6 attempts with packaged debug brief |

**Done when**: Solves ≥3 of 5 planted failures; always escalates cleanly when capped.
**Estimate**: 2 weeks · **Target finish**: Jan 16, 2027
