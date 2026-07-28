# Internal Data Analyst for Business Intelligence

**Layer**: Context Engineering (2024–2025)

## Goal
Non-technical stakeholders ask questions like "Which regions underperformed in Q3?" and get accurate answers

## Architecture
- Retrieve: database schema, recent metrics, business definitions
- Pass: definitions of KPIs (what is "ARR"? How is it calculated?), recent dashboards, known issues with data quality
- Model writes SQL or interprets dashboards
- Returns answer with context ("Based on data as of July 29, not including the known sync issue in EU region")

## Context Elements
- Schema documentation
- Metric definitions (reconciles disagreements about what "revenue" means)
- Recent anomalies ("Sales spike on July 15 was a one-time deal, not a trend")
- Known data quality issues
- Seasonal patterns
- Historical context ("Q2 baseline was X")

## Advantage
No more "the dashboard says 50K, but marketing says 55K"—everyone uses the same definitions. Answers are contextualized, not naive.

## When to Use This Layer
- Your domain has specialized knowledge (internal APIs, company definitions, architectural patterns)
- You want consistent, accurate answers grounded in your reality
- You have structured data (schemas, docs, policies) worth indexing
- Single-turn or simple back-and-forth interactions
- You need citations/traceability
