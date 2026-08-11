# Agentic Email Workflow Engine — Build Plan

## Context
This project has evolved significantly from its original scope. It started as a simple single-prompt email classifier (Project #1 of a 21-project AI Engineering curriculum, see `0. Build Order.md`), then was redesigned as a rigorous eval-driven classifier, and has now been reframed by the user into something much bigger: an **agentic, multi-tool email workflow engine** — emails are ingested on a schedule, understood, decomposed into tasks, routed dynamically to specialized sub-agents (each with its own tools — Postgres, SharePoint, CRM, vector/graph DBs, blob storage, etc.), results are aggregated into a draft, and a human approves before anything is sent/executed.

The README (`1. Prompt Engineering/Email Classification Service/README.md`) has already been rewritten to reflect this: problem statement, architecture diagram, and a 7-phase / 8-week build plan. The project folder is still empty except for the README — no code exists yet.

The user explicitly wants **dynamic, extensible routing** — new sub-agents, tools, and storage backends (vector DBs, graph DBs, MongoDB, S3, Azure Blob, not just Postgres) should be pluggable without rewriting the orchestrator. This plan is the concrete engineering design for that.

**Decisions confirmed with user in this session:**
- **Orchestration framework**: LangGraph (graph-based state machine, built-in persistence/checkpointing — avoids hand-rolling a state machine while still exposing the mechanics via nodes/edges)
- **Phase 1 tool scope**: All connectors (Postgres, SharePoint, CRM, email sender) start as **mocks/stubs** returning fixture data — unblocks building the orchestration logic without needing real external accounts first
- **Storage abstraction**: Start with **Postgres + pgvector** as the default vector store (reuses one DB for both structured data and embeddings), but the tool/storage layer must be built as a **pluggable interface** from day one so Chroma, a graph DB (e.g., Neo4j), MongoDB, S3, and Azure Blob can be added later as alternate implementations without touching agent or orchestrator code
- **Routing strategy** (from earlier discussion): Hybrid — tag-based matching first (fast, deterministic), semantic/vector search as fallback for ambiguous tasks, human escalation as the ultimate fallback

---

## Proposed Project Structure

```
1. Prompt Engineering/Email Classification Service/     # folder name kept for now; README title is "Agentic Email Workflow Engine"
├── README.md                        # already updated — problem statement, architecture, 7-phase plan
├── pyproject.toml                    # deps: langgraph, langchain-core, litellm, fastapi, pydantic,
│                                      #       sqlalchemy, psycopg[binary], pgvector, pytest, python-dotenv
├── .env.example
├── docker-compose.yml                # local Postgres (+pgvector extension) for dev
├── src/
│   ├── agents/
│   │   ├── base.py                   # Agent protocol: name, capability_tags, capability_description, run()
│   │   ├── understanding_agent.py    # parses intent/entities/urgency from raw email
│   │   ├── decomposition_agent.py    # breaks understood email into subtasks + dependencies
│   │   ├── database_agent.py         # queries DatabaseTool
│   │   ├── sharepoint_agent.py       # queries DocumentStoreTool
│   │   ├── crm_agent.py              # queries CRMTool
│   │   ├── aggregation_agent.py      # synthesizes results from multiple agents
│   │   └── draft_agent.py            # generates the response draft + action list
│   │
│   ├── tools/
│   │   ├── base.py                   # Tool protocol (name, capability_tags, call())
│   │   ├── registry.py               # ToolRegistry: register(tool), get(name), list_by_tag(tag)
│   │   ├── database_tool.py          # Postgres impl; interface allows swapping to Mongo later
│   │   ├── vector_store_tool.py      # pgvector impl behind a VectorStore protocol (swap: Chroma, etc.)
│   │   ├── document_store_tool.py    # mock SharePoint impl behind a DocumentStore protocol
│   │   ├── crm_tool.py               # mock CRM impl
│   │   ├── blob_store_tool.py        # stub protocol only in Phase 1 (S3/Azure Blob impls later)
│   │   └── email_sender_tool.py      # mock impl in Phase 1 (SMTP/API impl later)
│   │
│   ├── routing/
│   │   ├── agent_registry.py         # AgentRegistry: register(agent) at startup, list agents + tags
│   │   ├── tag_router.py             # fast tag-overlap matching: task requirements -> candidate agents
│   │   └── semantic_router.py        # fallback: embed task, search vector store of agent capability embeddings
│   │
│   ├── orchestrator/
│   │   ├── graph.py                  # LangGraph StateGraph definition: nodes = agents, edges = routing logic
│   │   ├── state.py                  # WorkflowState (Pydantic): email, understanding, subtasks, results, draft, approval, status
│   │   └── checkpoint.py             # persistence config (LangGraph checkpointer, e.g. Postgres-backed)
│   │
│   ├── ingestion/
│   │   └── scheduler.py              # polls IMAP (mock in Phase 1) on an interval, enqueues workflows
│   │
│   ├── api.py                        # FastAPI: POST /workflows (trigger), GET /workflows/{id} (status),
│   │                                  #          POST /workflows/{id}/approve, POST /workflows/{id}/reject
│   └── llm_client.py                 # LiteLLM wrapper, shared by all agents
│
├── eval/
│   ├── scenarios/                    # 20-30 end-to-end test emails w/ expected subtasks + expected agents invoked
│   ├── run_eval.py                   # runs scenarios through the graph, measures success rate/latency/cost
│   └── metrics.py
│
├── logs/                             # structured logs: per-node input/output/latency/cost, audit trail
└── tests/
    ├── test_agents.py                # each agent tested in isolation with mocked tools
    ├── test_routing.py               # tag_router + semantic_router correctness
    └── test_orchestrator.py          # graph wiring, state transitions, approval gate behavior
```

**Key design principle**: agents never import a concrete tool implementation directly — they call `tool_registry.get("database")` and get whatever implements the `DatabaseTool` protocol. Swapping Postgres → Mongo, or pgvector → Chroma, means writing one new class and registering it — zero changes to agent code. This is what makes the "not limited to Postgres" requirement real rather than aspirational.

---

## Phase-by-Phase Implementation Approach

### Phase 1 — Foundation: Protocols, Registry, Mocked Tools (Week 1)
1. Define `Agent` and `Tool` protocols (`src/agents/base.py`, `src/tools/base.py`) — this is the contract that makes the system pluggable. Every agent declares `capability_tags` (e.g. `["billing", "database_query"]`) and a natural-language `capability_description` (used later for semantic matching).
2. Build `ToolRegistry` and `AgentRegistry` — simple in-memory dict-based registries populated at startup (`main.py` registers each tool/agent once). This is the **startup registration** approach agreed on for Phase 1; runtime registration is a documented future extension, not built now.
3. Implement mocked tools first: `database_tool.py` (in-memory fixture data, same interface a real Postgres impl will have), `document_store_tool.py`, `crm_tool.py`, `email_sender_tool.py` — all return canned responses so the orchestration logic can be built and tested without external dependencies.
4. Stand up local Postgres via `docker-compose.yml` with the `pgvector` extension enabled, but don't wire it into any agent yet — this just proves the storage layer works in isolation (`tests/test_vector_store.py` style smoke test).
5. Build `eval/scenarios/`: 20-30 realistic end-to-end emails (support/sales/billing) with the expected subtask breakdown and expected agent(s) invoked — this is the ground truth the whole system is measured against going forward.

### Phase 2 — Core Agents (Weeks 2-3)
1. `understanding_agent.py`: single LLM call via `llm_client.py` that parses intent, entities, urgency from the raw email into a structured Pydantic object.
2. `decomposition_agent.py`: takes the understanding output, produces a list of subtasks, each tagged with `required_capabilities` (e.g. `["database_query", "customer_lookup"]`) and any dependency ordering.
3. `database_agent.py`, `sharepoint_agent.py`, `crm_agent.py`: each wraps one tool call + light reasoning (e.g. "does this result answer the subtask, or do I need to refine the query?").
4. `aggregation_agent.py`: takes all sub-agent outputs, synthesizes a coherent set of findings, flags conflicts.
5. `draft_agent.py`: produces the final email/response draft + explicit action list (e.g. "update CRM field X", "send this reply") with confidence scores.
6. Each agent tested independently against mocked tools in `tests/test_agents.py` — no orchestrator needed yet to validate agent logic in isolation.

### Phase 3 — Dynamic Routing (Week 4)
1. `tag_router.py`: given a subtask's `required_capabilities`, return agents from `AgentRegistry` whose `capability_tags` overlap — fast, deterministic, no LLM/embedding calls. This handles the common case.
2. `vector_store_tool.py`: pgvector-backed store of agent capability-description embeddings, built behind a `VectorStore` protocol (`embed_and_upsert`, `search`) so Chroma/other stores are drop-in alternatives later.
3. `semantic_router.py`: fallback path — only triggered when `tag_router` finds zero or ambiguous (multiple tied) candidates. Embeds the subtask description, searches the vector store, returns top-k agents with similarity scores.
4. Combine both in `routing/` with a single `route_subtask(subtask) -> Agent` entrypoint the orchestrator calls: try tags first, fall back to semantic, and if still no confident match, mark the subtask for human escalation rather than guessing.
5. `tests/test_routing.py`: verify tag matching, verify semantic fallback triggers correctly, verify escalation path when nothing matches.

### Phase 4 — Orchestration with LangGraph (Week 5)
1. `state.py`: define `WorkflowState` (Pydantic) — carries the email, understanding output, subtask list, per-subtask results, aggregated findings, draft, approval status, and full audit log of node transitions.
2. `graph.py`: build the LangGraph `StateGraph` — nodes for understanding → decomposition → a dynamic fan-out step (one node per routed subtask, executed in parallel where no dependency exists) → aggregation → draft → conditional edge to approval-wait.
3. Use LangGraph's checkpointing (Postgres-backed, reusing the same DB) so a workflow's state survives process restarts and can be resumed — this also gives you the audit trail for free.
4. `ingestion/scheduler.py`: simple interval-based poller (mocked IMAP source in Phase 1) that creates a new `WorkflowState` and invokes the graph for each new email.

### Phase 5 — Approval Gate & Execution (Week 6)
1. `api.py`: FastAPI endpoints — `POST /workflows` (manual trigger, for testing), `GET /workflows/{id}` (inspect current state incl. agent reasoning), `POST /workflows/{id}/approve` and `/reject` (resumes the paused LangGraph run via checkpoint).
2. The graph pauses at an `awaiting_approval` node (LangGraph interrupt) after the draft is generated — nothing is executed (no real email sent, no CRM updated) until approval is received.
3. On approval, a final `execution` node runs the approved actions through the (still-mocked in Phase 1) `email_sender_tool` / `crm_tool`, then transitions to `done`.
4. Every transition, agent call, and tool call is logged to `logs/` with input/output/latency/cost — this is the audit trail requirement from the README.

### Phase 6 — Evaluation & Iteration (Week 7)
1. `eval/run_eval.py`: runs all scenarios end-to-end through the graph (auto-approving in eval mode), measures: subtask decomposition accuracy, correct-agent-routed rate, end-to-end success rate, latency, cost per workflow.
2. Error analysis pass: categorize failures (wrong agent routed, tool returned bad data, aggregation conflict unresolved, draft quality poor) and iterate on the weakest agent/prompt.
3. Re-run eval after each fix to confirm improvement — same data-driven iteration discipline as the original classifier plan, just applied to a graph instead of a single prompt.

### Phase 7 — Production Hardening (Week 8)
1. Swap one mocked tool for a real implementation (start with `database_tool.py` → real Postgres queries) to prove the pluggable-tool design actually holds up against a real backend, without touching agent code.
2. Add monitoring: workflow success rate, per-agent failure rate, queue depth, cost dashboards (can be a simple logged-metrics script, not full observability infra).
3. Document architecture decisions, how to add a new agent/tool/storage backend (this becomes the extensibility guide — concretely: implement the protocol, register it, done).

---

## Key Libraries
- `langgraph` + `langchain-core` — orchestration graph, state management, checkpointing/persistence, human-in-the-loop interrupts
- `litellm` — provider-agnostic LLM calls, shared by every agent
- `pydantic` — all structured state and tool I/O
- `sqlalchemy` + `psycopg[binary]` + `pgvector` — Postgres access + vector store, both behind protocol interfaces
- `fastapi` + `uvicorn` — trigger/inspect/approve API
- `pytest` — agent, routing, and orchestrator tests (tools mocked throughout Phase 1-6)

## Verification Approach
- `tests/test_agents.py` — each agent tested in isolation against mocked tools (no LLM cost in CI if LLM calls are also mocked; live-LLM tests kept separate/optional).
- `tests/test_routing.py` — tag matching, semantic fallback, escalation path.
- `tests/test_orchestrator.py` — graph compiles, state transitions correctly, approval interrupt/resume works via checkpoint.
- `eval/run_eval.py` — primary end-to-end correctness signal; run after every agent/routing change, compare against the previous run's report (mirrors the original classifier plan's eval-driven discipline, scaled to a multi-agent graph).
- Manual smoke test: `uvicorn src.api:app`, POST a test email, inspect intermediate state via GET, approve, confirm mocked execution fires.

## Extensibility Guide (what "pluggable" means concretely)
- **New tool/storage backend** (e.g. Chroma, MongoDB, S3, Azure Blob, Neo4j): implement the relevant protocol in `src/tools/`, register an instance in `tool_registry` at startup. No orchestrator or agent changes required.
- **New agent**: implement the `Agent` protocol in `src/agents/`, declare its `capability_tags`, register it in `agent_registry` at startup. The router picks it up automatically for any subtask whose tags/semantics match.
- **Runtime (vs. startup) registration** is explicitly deferred — noted in the README/architecture as a Phase-beyond-8 extension once the startup-registration version is proven.

---

## Open Questions for Next Session
- Exact list of Phase 1 test scenario categories/emails — hand-written by user, or LLM-generated then reviewed?
- Whether LangGraph's built-in Postgres checkpointer should be used directly, or a custom checkpoint table alongside the app's own schema.
- Priority order for Phase 7's "swap one mock for real" — Postgres was assumed, but confirm before starting Phase 7.
