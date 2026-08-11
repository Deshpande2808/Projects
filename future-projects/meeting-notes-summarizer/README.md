# Meeting Notes Summarizer

**Layer**: Prompt Engineering (2022–2024)

## Goal
Transcribe meeting → extract summary + action items + attendees

## Approach
Prompt with template, parse structured output

## Limitations
No memory of previous meetings. Can't track follow-up on action items. Doesn't know project context, so summaries are generic.

## When to Use This Layer
- Demos and prototypes
- One-off analysis
- Interactive experiences where *you* are still in the loop between steps
- Tasks with no state or iteration

## Build Plan

**MVP**: Paste transcript → structured `{summary, action_items[], attendees[], decisions[]}`.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Template prompt | Fixed schema for summary + actions + owners + due dates |
| 2. Parsing hardening | Retry/repair when model returns invalid JSON |
| 3. Sample transcripts | 5–10 real/synthetic meetings across lengths |
| 4. Quality checks | Spot-check action-item completeness vs source |

**Done when**: Action items reliably include owner + verb; empty fields are explicit nulls, not invented.
**Estimate**: 4–5 days · **Target finish**: Aug 6, 2026
