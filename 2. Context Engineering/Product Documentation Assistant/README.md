# Product Documentation Assistant

**Layer**: Context Engineering (2024–2025)

## Goal
Answer customer questions about your product with current, accurate info. Never hallucinate pricing or features.

## Architecture
- Embed API docs, pricing tiers, feature list, SLAs, release notes
- On query: retrieve relevant sections
- Context includes: what the customer's plan is, what features they can access, what's recently changed
- Model answers with citations

## Context Pipeline
- Customer metadata (plan tier, features unlocked)
- API docs (structured, versioned)
- FAQ database
- Recent changelog (so it knows what's new)
- Company policies (what can be changed, what can't)

## Advantage
Answers are grounded in truth. No more "we don't know if that feature exists." Customers get accurate pricing, not guesses.

## When to Use This Layer
- Your domain has specialized knowledge (internal APIs, company definitions, architectural patterns)
- You want consistent, accurate answers grounded in your reality
- You have structured data (schemas, docs, policies) worth indexing
- Single-turn or simple back-and-forth interactions
- You need citations/traceability
