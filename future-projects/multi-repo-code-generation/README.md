# Multi-Repo Code Generation

**Layer**: Context Engineering (2024–2025)

## Goal
Write code in a monorepo that matches patterns across similar services

## Architecture
- Index multiple services: similar endpoints, middleware, error handling, test patterns
- On request: retrieve examples from 3 most similar existing services
- Context: "Here are three similar payment handlers. Model a new one."
- Model generates code matching your patterns

## Advantage
Consistency enforced by context, not by manual code review. New services adopt patterns automatically.

## Still Missing
Doesn't verify the code works. Doesn't run tests. Doesn't handle iteration if the generated code is wrong.

## When to Use This Layer
- Your domain has specialized knowledge (internal APIs, company definitions, architectural patterns)
- You want consistent, accurate answers grounded in your reality
- You have structured data (schemas, docs, policies) worth indexing
- Single-turn or simple back-and-forth interactions
- You need citations/traceability

## Build Plan

**MVP**: Given a new service request, pull examples from 2–3 similar services and generate matching handlers/tests/middleware.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Multi-index | Index ≥3 sibling services (endpoints, errors, tests) |
| 2. Similarity routing | Pick top-N analogous services per request |
| 3. Generation | Scaffold new service from those examples |
| 4. Consistency review | Diff against source patterns; checklist of shared conventions |

**Done when**: New scaffold compiles/imports correctly against shared libs and mirrors error-handling patterns.
**Estimate**: 2 weeks · **Target finish**: Oct 18, 2026
