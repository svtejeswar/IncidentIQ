# IncidentIQ — Folder Structure

```
incidentiq/
│
├── apps/
│   │
│   ├── backend/                           FastAPI Python service
│   │   │
│   │   ├── api/                           Presentation Layer (FastAPI adapters)
│   │   │   ├── routes/
│   │   │   │   ├── documents.py           Upload, list, delete documents + SSE stream
│   │   │   │   ├── search.py              Semantic search endpoint
│   │   │   │   ├── assistant.py           AI chat assistant endpoint
│   │   │   │   └── health.py              Health + readiness checks
│   │   │   │
│   │   │   ├── dependencies/
│   │   │   │   └── providers.py           DI wiring — FastAPI Depends factories
│   │   │   │
│   │   │   └── middleware/
│   │   │       └── cors.py                CORS configuration
│   │   │
│   │   ├── application/                   Application Layer (use cases + services)
│   │   │   ├── dto/
│   │   │   │   ├── document_dto.py        Pydantic models: DocumentCreateRequest, DocumentResponse
│   │   │   │   ├── search_dto.py          SearchRequest, SearchResponse, IncidentResult
│   │   │   │   └── assistant_dto.py       ChatRequest, ChatResponse, Message
│   │   │   │
│   │   │   ├── interfaces/                Port definitions (depend only on domain)
│   │   │   │   ├── llm_provider.py        ILLMProvider ABC
│   │   │   │   ├── embedding_provider.py  IEmbeddingProvider ABC
│   │   │   │   ├── vector_store_provider.py  IVectorStoreProvider ABC
│   │   │   │   └── file_storage.py        IFileStorage ABC
│   │   │   │
│   │   │   ├── services/                  Business orchestration
│   │   │   │   ├── document_service.py    Document lifecycle management
│   │   │   │   ├── search_service.py      Semantic search + RAG
│   │   │   │   └── ai_assistant_service.py  Conversational assistant
│   │   │   │
│   │   │   └── use_cases/                 Single-responsibility operations
│   │   │       ├── upload_document.py     Handle upload + trigger ingestion
│   │   │       ├── search_incidents.py    Execute semantic search
│   │   │       ├── find_similar_incidents.py  Vector similarity discovery
│   │   │       └── ask_assistant.py       RAG-based Q&A
│   │   │
│   │   ├── domain/                        Domain Layer (pure business — no framework deps)
│   │   │   ├── entities/
│   │   │   │   ├── document.py            Document aggregate root
│   │   │   │   ├── incident.py            Incident entity (extracted from docs)
│   │   │   │   └── chunk.py               Text chunk with embedding
│   │   │   │
│   │   │   ├── value_objects/
│   │   │   │   ├── document_type.py       DocumentType (INCIDENT_REPORT, RCA, RUNBOOK, ...)
│   │   │   │   └── severity.py            Severity (CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN)
│   │   │   │
│   │   │   ├── enums/
│   │   │   │   ├── document_status.py     PENDING | PROCESSING | COMPLETED | FAILED
│   │   │   │   └── processing_stage.py    UPLOADING | EXTRACTING | CHUNKING | EMBEDDING | ...
│   │   │   │
│   │   │   ├── repositories/              Abstract repository interfaces
│   │   │   │   ├── document_repository.py IDocumentRepository
│   │   │   │   ├── incident_repository.py IIncidentRepository
│   │   │   │   └── chunk_repository.py    IChunkRepository
│   │   │   │
│   │   │   └── exceptions/
│   │   │       └── domain_exceptions.py   DomainException hierarchy
│   │   │
│   │   ├── infrastructure/                Infrastructure Layer (concrete implementations)
│   │   │   ├── database/
│   │   │   │   ├── mongodb/
│   │   │   │   │   └── client.py          Motor async client + connection lifecycle
│   │   │   │   └── repositories/
│   │   │   │       ├── mongo_document_repository.py
│   │   │   │       ├── mongo_incident_repository.py
│   │   │   │       └── mongo_chunk_repository.py
│   │   │   │
│   │   │   ├── vector_store/
│   │   │   │   └── mongodb_vector/
│   │   │   │       └── mongo_vector_store.py  MongoDB Atlas $vectorSearch pipeline
│   │   │   │
│   │   │   ├── llm/
│   │   │   │   └── groq/
│   │   │   │       └── groq_provider.py   Groq API client (Llama3 / Qwen)
│   │   │   │
│   │   │   ├── embeddings/
│   │   │   │   └── sentence_transformer_provider.py  all-MiniLM-L6-v2
│   │   │   │
│   │   │   ├── file_processing/
│   │   │   │   ├── pdf_extractor.py       PyPDF2 text extraction
│   │   │   │   └── docx_extractor.py      python-docx text extraction
│   │   │   │
│   │   │   └── storage/
│   │   │       └── local_storage.py       Local filesystem storage (swap for S3)
│   │   │
│   │   ├── ingestion/                     Document Processing Pipeline
│   │   │   ├── extractors/
│   │   │   │   ├── base_extractor.py      BaseExtractor ABC
│   │   │   │   └── text_extractor.py      Format-aware text extraction dispatcher
│   │   │   │
│   │   │   ├── chunkers/
│   │   │   │   └── text_chunker.py        Sliding window chunker (512 tokens, 50 overlap)
│   │   │   │
│   │   │   ├── enrichers/
│   │   │   │   └── metadata_enricher.py   Extract services, severity, dates from text
│   │   │   │
│   │   │   └── pipelines/
│   │   │       └── document_pipeline.py   Orchestrates extract→chunk→enrich→embed→index
│   │   │
│   │   ├── mcp/                           MCP Layer stubs (V5 — do not implement yet)
│   │   │   └── tools/
│   │   │       └── incident_tools.py      search_incidents, find_similar, get_runbook, ask_assistant
│   │   │
│   │   ├── core/
│   │   │   ├── config/
│   │   │   │   └── settings.py            Pydantic Settings v2 (env-driven)
│   │   │   ├── logging/
│   │   │   │   └── logger.py              structlog configuration
│   │   │   └── constants/
│   │   │       └── constants.py           App-wide constants
│   │   │
│   │   ├── tests/
│   │   │   ├── unit/                      Pure domain + application tests
│   │   │   └── integration/               Infrastructure tests (real MongoDB)
│   │   │
│   │   ├── main.py                        App factory, lifespan, DI assembly
│   │   └── requirements.txt
│   │
│   └── frontend/                          Next.js 14 TypeScript app
│       ├── src/
│       │   ├── app/                       App Router pages
│       │   │   ├── layout.tsx             Root layout with Navbar
│       │   │   ├── page.tsx               Dashboard / home
│       │   │   ├── upload/page.tsx        Document upload page
│       │   │   ├── search/page.tsx        Semantic search page
│       │   │   └── assistant/page.tsx     AI chat page
│       │   │
│       │   ├── features/                  Feature-sliced UI components
│       │   │   ├── upload/
│       │   │   │   ├── UploadForm.tsx     Drag-drop upload with file type validation
│       │   │   │   └── ProcessingProgress.tsx  SSE-driven progress steps
│       │   │   ├── search/
│       │   │   │   ├── SearchBar.tsx      Natural language query input
│       │   │   │   ├── SearchResults.tsx  Results list with AI answer
│       │   │   │   └── IncidentCard.tsx   Individual result card
│       │   │   └── assistant/
│       │   │       ├── ChatInterface.tsx  Conversation UI
│       │   │       └── ChatMessage.tsx    Individual message bubble
│       │   │
│       │   ├── components/
│       │   │   ├── layout/
│       │   │   │   └── Navbar.tsx         Top navigation
│       │   │   └── ui/
│       │   │       └── StatusBadge.tsx    Document status chip
│       │   │
│       │   ├── hooks/
│       │   │   ├── useSSE.ts              Server-Sent Events subscription hook
│       │   │   ├── useSearch.ts           React Query search hook
│       │   │   └── useUpload.ts           Upload mutation hook
│       │   │
│       │   ├── services/
│       │   │   └── api.ts                 Typed API client (all endpoints)
│       │   │
│       │   ├── types/
│       │   │   └── index.ts               TypeScript interfaces matching backend DTOs
│       │   │
│       │   └── lib/
│       │       └── utils.ts               cn(), formatDate(), etc.
│       │
│       ├── public/
│       ├── package.json
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       └── tsconfig.json
│
├── docs/
│   ├── architecture/
│   │   ├── Architecture.md                This document's parent
│   │   └── Folder-Structure.md            This file
│   ├── api/
│   │   └── API-Design.md                  Full REST API contracts
│   ├── Development-Guide.md               Setup, running, testing
│   └── adr/                               Architecture Decision Records
│       ├── ADR-001-clean-architecture.md
│       ├── ADR-002-provider-pattern.md
│       ├── ADR-003-sse-realtime.md
│       └── ADR-004-mongodb-vector-search.md
│
├── scripts/                               One-off utilities, DB seeders
├── docker/                                Dockerfiles
├── .github/workflows/                     CI/CD pipelines
├── docker-compose.yml
├── .env.example
└── README.md
```
