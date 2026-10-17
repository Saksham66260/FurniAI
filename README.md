# FurniAI

> An AI-powered furniture commerce platform that combines grounded product intelligence with reliable e-commerce workflows.

FurniAI is a portfolio-grade modular monolith built to show how AI can improve discovery without taking authority away from the application. A shopper can search naturally, inspect why products ranked highly, ask grounded product questions, add items to a cart, and complete an approval-aware checkout flow.

![FurniAI storefront](frontend/src/assets/hero.png)

## Why this project stands out

- **Hybrid product discovery:** lexical and semantic search are combined into a deterministic ranking formula.
- **Explainable results:** every ranked product exposes semantic, keyword, rating, and price contributions.
- **Grounded AI assistant:** LangGraph orchestrates constrained backend tools; PostgreSQL remains authoritative.
- **Production-minded commerce flows:** inventory checks, transactional checkout, Redis-backed idempotency, and request observability.
- **Clear architecture:** a modular monolith keeps the system understandable while separating API, services, persistence, and agent layers.

## Architecture

```text
React + TypeScript
        │
        ▼
FastAPI API ─────── LangGraph shopping assistant
        │                         │
        ├── Application services ◄┘
        │       │
        │       ├── PostgreSQL + pgvector  (source of truth)
        │       └── Redis                  (cache + idempotency)
        │
        └── deterministic hybrid ranking
```

The ranking score is intentionally inspectable:

```text
0.50 × semantic similarity
+ 0.20 × keyword relevance
+ 0.15 × normalized rating
+ 0.15 × price preference
```

## Quick start

### Prerequisites

- Docker Desktop with Compose
- Node.js 20+
- Python 3.10+
- A Groq API key for the AI assistant (optional for non-AI catalog flows)

### 1. Configure the backend

```bash
cp backend/.env.example backend/.env
```

Add your `GROQ_API_KEY` to `backend/.env` if you want to use the assistant. The local defaults match the included Compose services.

### 2. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 3. Install and run the API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The API and interactive OpenAPI docs are available at [localhost:8000](http://localhost:8000) and [localhost:8000/docs](http://localhost:8000/docs).

### 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [localhost:5173](http://localhost:5173).

### Docker shortcut

After creating `backend/.env`, the full stack can be started with:

```bash
docker compose up --build
```

## API highlights

| Capability | Endpoint |
| --- | --- |
| Health check | `GET /health/db` |
| Product catalog | `GET /products/` |
| Lexical search | `GET /products/search?q=...` |
| Semantic search | `GET /products/semantic-search?q=...` |
| Explainable hybrid search | `GET /products/hybrid-search?q=...` |
| Product knowledge retrieval | `GET /products/{id}/knowledge?q=...` |
| AI assistant | `POST /agent/chat` |
| Cart and checkout | `/cart/*`, `/orders/*` |

## Verification

```bash
cd frontend
npm run lint
npm run build

cd ../backend
pytest -q
```

Integration tests expect the local PostgreSQL and Redis services plus seeded data to be available. The tests cover database health, observability headers, hybrid ranking, Redis-backed product retrieval, RAG knowledge retrieval, cart behavior, and the agent endpoint.

## Repository layout

```text
backend/app/api/          FastAPI route handlers
backend/app/services/     business logic and ranking
backend/app/agent/        LangGraph state, tools, and workflow
backend/alembic/          database migrations
backend/tests/            unit and integration tests
frontend/src/             React pages, components, and API client
docker-compose.yml        PostgreSQL, Redis, API, and frontend services
```

## Design decisions

FurniAI deliberately avoids microservices, Kubernetes, custom recommendation-model training, and direct database access from the LLM. The goal is a system that is explainable, testable, and easy to evolve while still demonstrating meaningful AI engineering.

## Roadmap

- Add Playwright browser coverage for the primary shopping journey.
- Add structured tracing for agent tool calls and search latency.
- Add authenticated user sessions instead of the demo user flow.
- Add deployment manifests and a managed Postgres/Redis environment.

## License

This repository is currently intended as a portfolio and technical demonstration project. Add a license before publishing if you plan to accept external contributions or reuse it commercially.
