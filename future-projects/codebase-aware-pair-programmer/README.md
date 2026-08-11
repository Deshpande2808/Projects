# Codebase-Aware Pair Programmer

**Layer**: Context Engineering (2024–2025)

## Goal
Help developers write code that matches your repo's patterns, uses your internal libraries, follows your architecture

## Architecture
- Index entire codebase (file paths, function signatures, recent commits)
- On query: retrieve similar files, recent changes, architectural patterns
- Pass curated context to model
- Model writes code that fits your style

## Key Context Elements
- Similar functions from your codebase (as examples)
- Your tech stack and dependencies
- Naming conventions, folder structure
- Internal APIs and utilities
- Architecture diagrams
- Recent commits (what changed and why)

## Advantage over Prompt Engineering
The model understands your system, not just English. New developers onboard faster. Code quality improves because it's grounded in your reality.

## Limitations
Still single-turn (or simple loops). No verification that code actually compiles/tests. No state across sessions.

## When to Use This Layer
- Your domain has specialized knowledge (internal APIs, company definitions, architectural patterns)
- You want consistent, accurate answers grounded in your reality
- You have structured data (schemas, docs, policies) worth indexing
- Single-turn or simple back-and-forth interactions
- You need citations/traceability

## Key Techniques
- Semantic search: Embed documents, retrieve by meaning not keyword match
- Metadata tagging: Tag which contexts apply to which queries
- Tiering: Put high-priority docs first in context
- Freshness tracking: Know when context is stale
- Citation: Return which documents informed the answer

## Build Plan

**MVP**: Ask for a function/feature → code that matches repo patterns (naming, libs, folder layout) using indexed codebase context.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Index | Paths, signatures, key modules, recent commits |
| 2. Retrieve | Similar implementations + conventions for the query |
| 3. Generate | Code grounded in retrieved examples |
| 4. Style check | Side-by-side vs real repo files on 5 tasks |

**Done when**: Generated code uses real internal APIs/patterns from the indexed repo on majority of tasks.
**Estimate**: 2.5 weeks · **Target finish**: Oct 4, 2026
