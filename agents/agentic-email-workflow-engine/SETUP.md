# Project Setup Guide

## Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

## Installation

### 1. Clone & Environment Setup
```bash
cd agents/agentic-email-workflow-engine

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=your_key_here
```

### 2. Start Database (Postgres + pgvector)
```bash
docker-compose up -d

# Verify it's running
docker-compose ps

# Should see:
# agentic-email-engine-db    pgvector/pgvector:pg16-latest    Up (healthy)
```

### 3. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Or with dev tools:
pip install -e ".[dev]"
```

### 4. Verify Setup
```bash
# Check database connection
python -c "from src.config import settings; print(f'Database URL: {settings.database_url}')"

# Run tests (should all pass or skip)
pytest tests/ -v
```

## Development Workflow

### Running Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src  # With coverage
```

### Starting the API (after Phase 5)
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Stopping the Database
```bash
docker-compose down
```

### Cleaning Everything
```bash
docker-compose down -v  # -v removes volumes
rm -rf __pycache__ .pytest_cache .coverage
```

## Project Structure

```
.
├── pyproject.toml              # Dependencies & project config
├── .env.example                # Environment variables template
├── docker-compose.yml          # Postgres + pgvector setup
├── SETUP.md                    # This file
├── README.md                   # Project description
│
├── scripts/
│   └── init-pgvector.sql       # Database schema initialization
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Settings & configuration
│   ├── agents/                 # Agent implementations (Phase 2)
│   ├── tools/                  # Tool integrations (Phase 1)
│   ├── routing/                # Dynamic routing logic (Phase 3)
│   ├── orchestrator/           # LangGraph orchestration (Phase 4)
│   ├── ingestion/              # Email scheduler (Phase 4)
│   ├── api.py                  # FastAPI server (Phase 5)
│   └── llm_client.py           # LiteLLM wrapper (Phase 2)
│
├── eval/
│   ├── scenarios/              # Test emails & expected outcomes (Phase 1)
│   ├── reports/                # Evaluation results (Phase 6)
│   ├── run_eval.py             # Evaluation runner (Phase 1)
│   └── metrics.py              # Metrics calculation (Phase 1)
│
├── logs/                       # Runtime logs & audit trails (Phase 5+)
│
└── tests/
    ├── test_agents.py          # Agent unit tests (Phase 2)
    ├── test_routing.py         # Router tests (Phase 3)
    └── test_orchestrator.py    # Graph tests (Phase 4)
```

## Common Issues

### Database Connection Failed
```
Error: could not translate host name "postgres" to address
```
**Solution**: Make sure Docker container is running: `docker-compose ps`

### pgvector Extension Not Found
```
ERROR: pgvector is not installed
```
**Solution**: We're using `pgvector/pgvector:pg16-latest` image which includes it. Rebuild: `docker-compose down -v && docker-compose up`

### Python Virtual Environment Issues
```
command not found: python
```
**Solution**: Activate venv: `source venv/bin/activate`

## Next Steps

See `../../Plans/agentic-email-workflow-engine/plan.md` for the 8-week implementation roadmap.

**Phase 1 (Week 1)**: Foundation protocols, registries, mocked tools
**Phase 2 (Weeks 2-3)**: Core agent implementations
**Phase 3 (Week 4)**: Dynamic routing
**Phase 4 (Week 5)**: LangGraph orchestration
**Phase 5 (Week 6)**: Approval gates & execution
**Phase 6 (Week 7)**: Evaluation & iteration
**Phase 7 (Week 8)**: Production hardening
