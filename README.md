# evidence-rag
## Quick start

```bash
docker compose up -d db            # Postgres + pgvector on localhost:5434
cd backend && uv sync
uv run uvicorn evidencerag.interfaces.api.app:create_app --factory --reload
```

Health check: http://127.0.0.1:8000/api/v1/health
