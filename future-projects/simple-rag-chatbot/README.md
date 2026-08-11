# Simple RAG Chatbot

**Layer**: Prompt Engineering (2022–2024)

## Goal
"Chat with your docs"—load PDFs, retrieve relevant sections, answer questions

## Architecture
- Embed documents
- On query: retrieve top-k relevant chunks
- Pass chunks + query to model
- Model answers

## Limitations
No memory between sessions. Retrieval quality directly limits answer quality. No verification—if retrieval fails, you get hallucinations. Doesn't handle follow-up or clarification well.

## When to Use This Layer
- Demos and prototypes
- One-off analysis
- Interactive experiences where *you* are still in the loop between steps
- Tasks with no state or iteration

## Build Plan

**MVP**: Upload PDFs → ask questions → answers grounded in retrieved chunks (no citations required yet).

| Milestone | Deliverable |
|-----------|-------------|
| 1. Ingest | Chunk + embed a small doc set (e.g. 5–10 PDFs) |
| 2. Retrieve | Top-k similarity search; tune chunk size/overlap |
| 3. Answer | Prompt that only uses retrieved context |
| 4. Eval | 20 Q&A pairs; measure groundedness vs hallucination |

**Done when**: Answers refuse when retrieval is empty; retrieval quality is the documented bottleneck (bridges to Context Engineering).
**Estimate**: 1.5 weeks · **Target finish**: Aug 24, 2026
