# Development Guide

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12+ | [python.org](https://python.org) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) |
| Git | any | [git-scm.com](https://git-scm.com) |

**External services required:**
- MongoDB Atlas cluster (free tier works)
- Groq API key (free at console.groq.com)

---

## Local Setup

### 1. Repository

```bash
git clone <repo-url>
cd incidentiq
cp .env.example .env
```

Edit `.env` and fill in:
- `MONGODB_URI` — your Atlas connection string
- `GROQ_API_KEY` — your Groq key

### 2. MongoDB Atlas Setup

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Add your IP to the allowlist (Network Access)
3. Create a database user
4. Copy the connection string to `MONGODB_URI`
5. Create the vector search index (see below)

**Create Vector Search Index:**

In Atlas UI → Search → Create Search Index → JSON editor:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "document_id"
    },
    {
      "type": "filter",
      "path": "document_type"
    }
  ]
}
```

Index name: `incidentiq_vector_index`
Collection: `chunks`

### 3. Backend

```bash
cd apps/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs for the interactive API docs.

### 4. Frontend

```bash
cd apps/frontend

# Install dependencies
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run development server
npm run dev
```

Visit http://localhost:3000

---

## Project Structure Quick Reference

```
apps/backend/
├── domain/          ← Pure business logic — edit entities, rules here
├── application/     ← Use cases and services — edit orchestration here
├── infrastructure/  ← Swap MongoDB/Groq/etc here
├── api/             ← HTTP routes — thin adapters only
└── ingestion/       ← Document processing pipeline

apps/frontend/
├── features/        ← Add new UI features here (feature-sliced)
├── hooks/           ← Data fetching and SSE hooks
└── services/api.ts  ← All API calls go through here
```

---

## Running Tests

```bash
cd apps/backend

# Unit tests (no external services needed)
pytest tests/unit/ -v

# Integration tests (requires MongoDB)
pytest tests/integration/ -v --mongodb-uri=$MONGODB_URI

# All tests
pytest tests/ -v --cov=. --cov-report=html
```

---

## Adding a New Document Type

1. Add the type to `domain/value_objects/document_type.py`
2. Add extractor logic in `ingestion/extractors/text_extractor.py` if needed
3. Update `application/dto/document_dto.py` to include the new type in the enum
4. No other changes needed — the pipeline handles it generically

## Swapping the LLM Provider

1. Create `infrastructure/llm/<provider>/<provider>_provider.py`
2. Implement `ILLMProvider` interface
3. Update `api/dependencies/providers.py` to inject the new provider
4. Zero application logic changes

## Swapping the Vector Store

1. Create `infrastructure/vector_store/<provider>/<provider>_vector_store.py`
2. Implement `IVectorStoreProvider` interface
3. Update `api/dependencies/providers.py`
4. Zero application logic changes

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URI` | Yes | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | No | Database name (default: `incidentiq`) |
| `GROQ_API_KEY` | Yes | Groq API key |
| `GROQ_MODEL` | No | Model ID (default: `llama3-70b-8192`) |
| `EMBEDDING_MODEL` | No | HuggingFace model ID |
| `VECTOR_DIMENSIONS` | No | Embedding dimensions (default: 384) |
| `VECTOR_INDEX_NAME` | No | Atlas vector index name |
| `UPLOAD_DIR` | No | File storage path |
| `MAX_FILE_SIZE_MB` | No | Max upload size (default: 50) |
| `ALLOWED_ORIGINS` | No | CORS origins (comma-separated) |
| `DEBUG` | No | Enable debug logging |

---

## Code Conventions

- **No business logic in routes** — routes call use cases only
- **No direct DB calls in services** — use repository interfaces
- **No framework imports in domain** — domain is pure Python
- **Async everywhere** — all I/O operations are async
- **Pydantic v2 for all DTOs** — use `model_config = ConfigDict()`
- **Type hints on all functions** — no untyped signatures

## Git Workflow

```bash
# Feature branch
git checkout -b feature/your-feature-name

# Commit (use conventional commits)
git commit -m "feat: add similar incident discovery endpoint"
git commit -m "fix: handle corrupted PDF extraction"
git commit -m "refactor: extract chunker into separate module"

# Push
git push origin feature/your-feature-name
```
