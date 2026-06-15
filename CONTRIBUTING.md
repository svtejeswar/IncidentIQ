# Contributing to IncidentIQ

Thank you for your interest in contributing. This document covers everything you need to get from zero to a merged pull request.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Branch Strategy](#branch-strategy)
- [Commit Messages](#commit-messages)
- [Running Tests](#running-tests)
- [Pull Request Process](#pull-request-process)
- [Architecture Rules](#architecture-rules)
- [Code Style](#code-style)

---

## Development Setup

### Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
# Fill in MONGODB_URI, GROQ_API_KEY, APP_SECRET_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd apps/frontend
npm install
# Create .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
```

---

## Branch Strategy

| Branch pattern | Purpose |
|---|---|
| `main` | Production-ready code only |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Maintenance (deps, config, docs) |
| `refactor/<name>` | Code refactors with no behavior change |

Always branch off `main`. Open a PR back to `main`.

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/).

```
<type>(<scope>): <short description>

[optional body]
```

**Types**: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

**Scopes**: `backend`, `frontend`, `ingestion`, `search`, `assistant`, `infra`, `docs`

Examples:

```
feat(search): add document_types filter to semantic search endpoint
fix(ingestion): handle empty PDF pages without crashing
chore(deps): upgrade groq to 0.14.0
test(backend): add integration tests for document upload route
```

---

## Running Tests

```bash
cd apps/backend
source .venv/bin/activate

# All tests
pytest

# Unit tests only (no external dependencies — fast)
pytest tests/unit/ -v

# Integration tests (mocked deps)
pytest tests/integration/ -v

# With coverage
pytest --cov=. --cov-report=term-missing
```

All tests must pass before a PR can be merged.

---

## Pull Request Process

1. Fork the repo and create a branch from `main`
2. Write tests for any new functionality
3. Ensure all tests pass: `pytest`
4. Ensure the frontend type-checks: `npm run type-check`
5. Open a PR with a clear title following the commit format
6. Fill in the PR template — describe what changed and why
7. Link any related issues

PRs need one approving review before merge.

---

## Architecture Rules

IncidentIQ uses Clean Architecture. These rules are non-negotiable:

1. **Dependencies point inward.** `domain/` imports nothing from `application/`, `infrastructure/`, or `api/`. `application/` imports from `domain/` only.
2. **No framework imports in domain.** `domain/entities/`, `domain/value_objects/`, and `domain/repositories/` must not import FastAPI, Motor, Pydantic, or any infrastructure library.
3. **Infrastructure implements interfaces.** Every new external service (LLM, storage, vector DB) must implement an interface defined in `application/interfaces/`. The concrete class lives in `infrastructure/`.
4. **Use cases are thin.** Use cases in `application/use_cases/` delegate to services. They contain no business logic themselves.
5. **Routes contain no business logic.** API routes call use cases or services and return DTOs. Nothing else.

If you're unsure where a new piece of code belongs, read [docs/architecture/Architecture.md](docs/architecture/Architecture.md) or open a discussion issue first.

---

## Code Style

### Python

- Python 3.12+ type hints on all functions and class fields
- `from __future__ import annotations` at the top of every file
- `async/await` throughout — no blocking I/O on the event loop
- Docstrings only when the WHY is non-obvious; omit otherwise
- No bare `except:` — always catch specific exceptions
- structlog for logging — never `print()`

### TypeScript / React

- Strict TypeScript — no `any`
- `"use client"` only on components that require browser APIs or hooks
- Prefer server components for static content
- Custom hooks for any stateful logic
- Tailwind CSS utility classes only — no inline `style` for colors (use CSS variables)

---

## Questions?

Open a [GitHub Discussion](../../discussions) or file an issue. We're happy to help.
