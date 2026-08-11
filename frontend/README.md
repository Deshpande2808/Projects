# Unified AI Agent Frontend

**Status**: Placeholder / Under Planning (to be built after core agents are complete)

## Purpose

This is the unified web interface where users come to interact with any AI agent in the system. Currently a placeholder; actual development will begin once the first few agents (starting with the Agentic Email Workflow Engine) are working.

## Architecture (Planned)

The frontend will:
- List all available agents (fetched from agent registry/API)
- Allow users to select an agent
- Display a dynamic form/interface based on the selected agent's input schema
- Execute the agent workflow
- Display results, progress, and execution history
- Manage authentication and user context

## Agent Integration Pattern

Each agent exposes an API (e.g., via FastAPI) with:
- `GET /agent/info` — metadata (name, description, input schema, output schema)
- `POST /agent/run` — trigger execution, returns task ID
- `GET /agent/status/{task_id}` — poll for completion
- `GET /agent/result/{task_id}` — fetch results

The frontend dynamically calls these endpoints based on which agent is selected.

## Folder Structure

```
frontend/
├── README.md               # This file
├── public/                 # Static assets (placeholder)
├── src/                    # Source code (placeholder)
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── utils/
└── package.json            # Will be created during setup
```

## Technology Stack (To Be Decided)

- Framework: React / Vue / Next.js (TBD)
- Styling: Tailwind / Material UI (TBD)
- State management: Redux / Context / Zustand (TBD)
- API client: axios / fetch (TBD)

## When to Build

After the first 2-3 agents are complete and working via their APIs, integrate them into this frontend as a unified hub.

---

**See Also**: `../Plans/agentic-email-workflow-engine/plan.md` for the current agent in development.
