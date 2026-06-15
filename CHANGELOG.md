# Changelog

All notable changes to IncidentIQ are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2025-06-14

### Added

**Backend**
- FastAPI application with Clean Architecture (Domain → Application → Infrastructure → Presentation)
- Document upload endpoint — PDF, DOCX, TXT, Markdown up to 50 MB
- 8-stage async ingestion pipeline: Extract → Chunk → Enrich → Embed → Index
- Server-Sent Events (SSE) for real-time pipeline progress streaming
- Sliding window text chunker (512 words, 50-word overlap)
- Regex-based metadata enricher: severity, root cause, resolution, affected services
- SentenceTransformer embedding provider (`all-MiniLM-L6-v2`, 384 dimensions)
- MongoDB Atlas Vector Search integration via `$vectorSearch` aggregation
- Semantic search endpoint with optional RAG-generated answers (Groq Llama 3.3 70B)
- Similar incident discovery by document ID or free-text query
- AI assistant chat endpoint with conversational RAG context
- Platform statistics endpoint (live document and chunk counts from MongoDB)
- Health liveness and readiness endpoints
- Structured logging via structlog (console in dev, JSON in production)
- Pydantic v2 settings with environment variable configuration
- Repository pattern with abstract interfaces for all external dependencies
- FastAPI dependency injection for all service and use case composition
- MCP Server tool stubs for V5 integration
- Architecture Decision Records (ADR-001 through ADR-004)

**Frontend**
- Next.js 15 App Router application with TypeScript
- Custom design system using Tailwind CSS v3 and CSS custom properties
- Dark / light theme switching via `next-themes` with localStorage persistence
- Landing page with real-time platform statistics, pipeline visualization, and feature overview
- Document upload page with SSE progress display
- Semantic search page with AI answer panel and incident result cards
- AI assistant page with full-height chat interface and source citations
- Responsive navbar with context-aware navigation (landing vs. app mode)
- Custom hooks: `useSearch`, `useStats`, `useSSE`
- Typed API client (`services/api.ts`) covering all backend endpoints

**Infrastructure**
- Docker Compose setup for local development
- `.env.example` with all required variables documented
- `.gitignore` covering Python, Node, IDE, OS, and upload artifacts

### Architecture

- Clean Architecture with strict inward dependency rule
- Provider pattern for LLM, embedding, vector store, and file storage — all swappable
- Repository pattern for all persistence operations
- Use cases as thin command handlers delegating to services
- SSE streaming integrated at the route layer, not the domain layer

---

## Planned

### [1.1.0]
- Authentication and authorization layer
- Rate limiting middleware

### [2.0.0]
- Service dependency visualization
- Incident timeline analytics

See [README.md — Roadmap](README.md#roadmap) for the full V2–V10 plan.
