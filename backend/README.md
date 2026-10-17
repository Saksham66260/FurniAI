# FurniAI API

FastAPI service for FurniAI's catalog, hybrid search, cart, checkout, inventory, and AI shopping assistant workflows.

```bash
cp backend/.env.example backend/.env
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://localhost:8000/docs`.

The service keeps business rules in application services, PostgreSQL as the source of truth, Redis for cache/idempotency support, and deterministic Python ranking for search results. The LangGraph agent can call constrained backend tools, but it does not access the database directly.
