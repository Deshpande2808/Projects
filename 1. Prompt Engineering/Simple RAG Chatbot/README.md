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
