# Report Generation with Validation

**Layer**: Loop Engineering (2026)

## Goal
Agent ingests raw field data (photos, voice memos, written notes) → drafts structured report → validates against schema → corrects → human reviews → hands off.

## Loop Structure
```
OBSERVE:
  - Read raw field inputs (images, text, voice transcription)
  - Fetch schema (what fields are required? format rules?)
PLAN:
  - Which raw inputs map to which schema fields?
  - What transformations are needed?
ACT:
  - Draft report in schema-compliant JSON
  - Extract structured data from unstructured inputs
VERIFY:
  - Schema validation: Does JSON match required format?
  - Completeness: Are all required fields present?
  - Correctness: Do extracted values make sense? (e.g., date in future = error)
  - Quality: Any obviously wrong extractions? (e.g., site name = "null"?)
LOOP:
  - If validation fails: Regenerate missing/wrong fields, re-validate
  - If correctness check fails: Fix interpretation, re-extract
  - After 3 failures: Escalate; mark fields as needing human review
  - If all passes: Ready for human sign-off
```

## Example: Site Inspection Report
- Raw data: photos of building damage, voice memo describing issues, handwritten checklist
- Schema: {property_address, damage_type, severity, repair_estimate, inspector_notes}
- Loop: Extract damage types from photos → cross-check with voice memo → fill in structured fields → verify all required fields present → send to adjuster

## When to Use This Layer
- Tasks lasting minutes to hours
- Verification is possible (tests, schemas, external feedback)
- Iteration improves quality
- Single agent doing complex work
- The task has a clear stopping condition ("tests pass", "schema valid", "performance target met")
