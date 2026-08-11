# Research Paper Writing Factory

**Layer**: Graph Engineering (July 2026)

## Goal
Produce research papers autonomously. Each specialized agent handles part of the work, hands off to next.

## Graph Structure
```
NODES (Agents):
  1. Researcher: Reads latest papers, summarizes trends
  2. Outliner: Takes trends → structures paper outline
  3. Writer: Expands outline into full sections
  4. Verifier: Checks citations, logic, evidence quality
  5. Editor: Polishes prose, catches errors
  6. Human: Reviews + provides feedback
EDGES (Handoffs):
  Start → Researcher → Outliner → Writer → Verifier → Editor → Human → End

  Feedback loops:
  - Verifier finds weak evidence → sends back to Writer for revision
  - Human requests changes → sends back to Editor
```

## Each Agent's Loop

**Researcher Loop**
- Observe: Research topic
- Plan: Which papers are most relevant? What trends are emerging?
- Act: Read papers, extract key findings
- Verify: Do findings coherently support a narrative?
- Loop: If findings are scattered, refocus on strongest thread

**Outliner Loop**
- Observe: Researcher's summary
- Plan: What's the thesis? What sections support it?
- Act: Draft outline
- Verify: Does outline flow logically? Are all key points covered?
- Loop: Refine structure until coherent

**Writer Loop**
- Observe: Outline + research summaries
- Plan: How to expand each section? What evidence belongs where?
- Act: Draft section text
- Verify: Is it well-sourced? Does it match outline? Is prose clear?
- Loop: Iterate until section is solid

**Verifier Loop**
- Observe: Sections + claims + citations
- Plan: Which claims need fact-checking? Are citations complete?
- Act: Verify each significant claim. Check citation formatting.
- Verify: Do citations actually support claims? (Read cited papers)
- Loop: If claim is weak, route back to Writer with feedback

**Editor Loop**
- Observe: Full manuscript
- Plan: Are there typos? Is tone consistent? Does prose flow?
- Act: Edit for clarity and consistency
- Verify: Did edits break meaning? Are citations still correct?
- Loop: Polish until production-ready

## State Across Edges
- Topic (static)
- Research findings (Researcher → Outliner → Writer)
- Outline (Outliner → Writer)
- Draft text (Writer → Verifier → Editor)
- Citation list (Researcher → Writer → Verifier → Editor)
- Feedback from verification (Verifier → Writer)

## Verification
Each node checks the previous node's work. If quality is low, reject and send back with feedback.

## When to Use This Layer
- Multiple agents with different expertise
- Workflow requires handoffs (agent A → agent B → agent C)
- Verification chains (each agent checks previous agent's work)
- Multi-step pipelines (data → analysis → decision → action)
- Enterprise-scale (needs audit trails, compliance, observability)

## Build Plan

**MVP**: Linear multi-agent pipeline Researcher → Outliner → Writer → Verifier → Editor with revision edges.

| Milestone | Deliverable |
|-----------|-------------|
| 1. Node contracts | Clear I/O schemas between agents |
| 2. Pipeline + loops | Verifier→Writer and Human→Editor feedback |
| 3. Citation check | Verifier flags weak/missing evidence |
| 4. Paper artifact | One short paper produced end-to-end |

**Done when**: Weak evidence triggers revision; human feedback re-enters the graph; final draft is coherent with citations.
**Estimate**: 3 weeks · **Target finish**: Mar 30, 2027
