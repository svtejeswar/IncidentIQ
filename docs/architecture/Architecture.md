# IncidentIQ — Architecture

## Overview

IncidentIQ follows **Clean Architecture** (Robert C. Martin). The core rule: **business logic never depends on infrastructure**. All dependencies point inward toward the domain.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                            │
│                                                                      │
│   ┌──────────────────────┐        ┌───────────────────────────────┐  │
│   │     Next.js UI       │        │     FastAPI Routes            │  │
│   │  Pages, Components   │◄──────►│  /api/v1/documents            │  │
│   │  React Query hooks   │  HTTP  │  /api/v1/search               │  │
│   └──────────────────────┘        │  /api/v1/assistant            │  │
│                                   └──────────────┬────────────────┘  │
└──────────────────────────────────────────────────┼───────────────────┘
                                                   │  calls via DTOs
┌──────────────────────────────────────────────────▼───────────────────┐
│                        APPLICATION LAYER                             │
│                                                                      │
│   ┌─────────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│   │ DocumentService  │  │  SearchService  │  │AIAssistantService │   │
│   └─────────────────┘  └─────────────────┘  └───────────────────┘   │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                       Use Cases                              │   │
│   │  UploadDocument | SearchIncidents | FindSimilar | AskAssist  │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   Depends on domain interfaces only — zero infrastructure coupling   │
└──────────────────────────────────────────────────────────────────────┘
             │ implements (via dependency inversion)
┌────────────▼─────────────────────────────────────────────────────────┐
│                          DOMAIN LAYER                                │
│                                                                      │
│  ┌───────────────────────┐    ┌────────────────────────────────────┐ │
│  │  Entities             │    │  Repository Interfaces (ABC)       │ │
│  │  • Document           │    │  • IDocumentRepository             │ │
│  │  • Incident           │    │  • IIncidentRepository             │ │
│  │  • Chunk              │    │  • IChunkRepository                │ │
│  └───────────────────────┘    └────────────────────────────────────┘ │
│                                                                      │
│  ┌───────────────────────┐    ┌────────────────────────────────────┐ │
│  │  Value Objects        │    │  Provider Interfaces (ABC)         │ │
│  │  • DocumentType       │    │  • ILLMProvider                    │ │
│  │  • Severity           │    │  • IEmbeddingProvider              │ │
│  └───────────────────────┘    │  • IVectorStoreProvider            │ │
│                               │  • IFileStorage                    │ │
│  Zero framework dependencies  └────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
             │ implemented by
┌────────────▼─────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER                            │
│                                                                      │
│  ┌────────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │  MongoDB           │  │  Groq LLM        │  │ SentenceTransf.  │  │
│  │  Repositories      │  │  Provider        │  │ EmbeddingProv.   │  │
│  └────────────────────┘  └─────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌────────────────────┐  ┌─────────────────────────────────────────┐ │
│  │  MongoDB           │  │         Ingestion Pipeline              │ │
│  │  VectorStore       │  │  Extract → Chunk → Embed → Index        │ │
│  └────────────────────┘  └─────────────────────────────────────────┘ │
│                                                                      │
│  Future: QdrantVectorStore | GeminiProvider | OpenAIProvider         │
└──────────────────────────────────────────────────────────────────────┘

                      ┌──────────────────────────┐
                      │       MCP Layer          │   ← Future V5
                      │  Calls App Layer only    │
                      │  search_incidents()      │
                      │  find_similar()          │
                      │  get_runbook()           │
                      │  ask_assistant()         │
                      └──────────────────────────┘
```

---

## Document Processing Flow

```
HTTP POST /api/v1/documents/upload
          │
          ▼
    [DocumentsRoute]
    validates file type/size
          │
          ▼
    [UploadDocumentUseCase]
    ├─ FileStorage.save(file) → file_path
    ├─ DocumentRepository.save(Document{PENDING})
    ├─ Returns document_id immediately (202 Accepted)
    └─ Spawns background task → IngestionPipeline
          │
          ▼ (async background)
    [DocumentIngestionPipeline]
    │
    ├── Stage 1: Extract          SSE event: {stage: "extracting"}
    │   └── BaseExtractor.extract(file_path) → raw_text
    │
    ├── Stage 2: Chunk            SSE event: {stage: "chunking"}
    │   └── TextChunker.chunk(raw_text) → [Chunk, ...]
    │
    ├── Stage 3: Enrich           SSE event: {stage: "enriching"}
    │   └── MetadataEnricher.enrich(chunks) → annotated chunks
    │
    ├── Stage 4: Embed            SSE event: {stage: "embedding"}
    │   └── EmbeddingProvider.encode([text, ...]) → [vector, ...]
    │
    ├── Stage 5: Index            SSE event: {stage: "indexing"}
    │   └── VectorStoreProvider.upsert(chunks_with_embeddings)
    │       ChunkRepository.save_batch(chunks)
    │
    └── Complete                  SSE event: {stage: "completed"}
        DocumentRepository.update(status: COMPLETED, chunk_count: N)
```

---

## RAG Search Flow

```
GET /api/v1/search?q=database+connection+timeouts
          │
          ▼
    [SearchRoute] → SearchIncidentsUseCase
          │
          ▼
    [SearchService]
    │
    ├── EmbeddingProvider.encode(query) → query_vector[384]
    │
    ├── VectorStoreProvider.similarity_search(query_vector, k=10)
    │   └── MongoDB $vectorSearch pipeline → [ScoredChunk, ...]
    │
    ├── Rerank: group by document_id, take top chunks per doc
    │
    ├── Hydrate: DocumentRepository.get_by_ids([...]) → documents
    │
    ├── Build RAG context string from top chunks
    │
    └── LLMProvider.generate(system_prompt + context + query)
        └── Returns SearchResponse{answer, sources, similar_incidents}
```

---

## Key Design Patterns

### 1. Repository Pattern

Abstract data access behind interfaces. Application services never touch MongoDB directly.

```python
# Domain defines the contract
class IDocumentRepository(ABC):
    async def save(self, doc: Document) -> Document: ...
    async def get_by_id(self, id: UUID) -> Document | None: ...

# Infrastructure implements it
class MongoDocumentRepository(IDocumentRepository):
    async def save(self, doc: Document) -> Document:
        # Motor async MongoDB call
```

### 2. Provider Pattern

Infrastructure providers are swappable at the DI layer:

```python
class ILLMProvider(ABC):
    async def generate(self, messages, ...) -> LLMResponse: ...

# Current: GroqProvider
# Future: GeminiProvider | OpenAIProvider | OllamaProvider
```

### 3. Dependency Injection (FastAPI Depends)

All dependencies wired in `api/dependencies/providers.py`. Routes never instantiate infrastructure directly.

### 4. SSE for Realtime Updates

Document processing stages emit Server-Sent Events. The frontend subscribes to `/api/v1/documents/{id}/stream` and updates a progress UI in real-time.

### 5. MCP Readiness

The `mcp/tools/` layer contains stub tool implementations that call Application Services. When MCP V5 is built, only the MCP transport layer changes — zero business logic modifications needed.

---

## MongoDB Collections

```
incidentiq/
├── documents        # Uploaded document metadata + status
├── chunks           # Text chunks with embeddings (vector search target)
├── incidents        # Extracted structured incident records
└── users            # User accounts (future auth)
```

---

## Future Extension Points

| Extension | What to add | What stays the same |
|---|---|---|
| Qdrant Vector Search | `QdrantVectorStore(IVectorStoreProvider)` | All application services |
| Gemini LLM | `GeminiProvider(ILLMProvider)` | All search/assistant logic |
| Slack Bot | New presentation adapter calling app services | All business logic |
| MCP Server | New MCP tool wrappers calling app services | All business logic |
| Neo4j Knowledge Graph | New repository + service | Existing document/search services |
| JIRA Integration | New infrastructure adapter | All existing services |
