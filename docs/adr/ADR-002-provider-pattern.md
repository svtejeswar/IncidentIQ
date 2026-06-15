# ADR-002: Provider Pattern for LLM and Vector Store

**Status:** Accepted
**Date:** 2024-01-01

## Context

The initial stack uses Groq for LLM and MongoDB Atlas Vector Search. The spec explicitly requires that swapping to Gemini or Qdrant should need minimal changes.

## Decision

All external AI provider interactions go through abstract interfaces:
- `ILLMProvider` — `generate()`, `stream()`
- `IEmbeddingProvider` — `encode()`, `encode_batch()`
- `IVectorStoreProvider` — `upsert()`, `similarity_search()`
- `IFileStorage` — `save()`, `read()`, `delete()`

Concrete implementations live in `infrastructure/`. The DI container in `api/dependencies/providers.py` is the only place where concrete classes are instantiated.

## Consequences

**Positive:**
- `GroqProvider` → `GeminiProvider` requires changing one line in `providers.py`
- Application services are 100% decoupled from vendor SDKs
- Easy to write tests with mock providers

**Negative:**
- Interface design must be general enough — not too Groq-specific
- Streaming interfaces require careful async generator design

## Provider Hierarchy

```
ILLMProvider
├── GroqProvider           (V1 — current)
├── GeminiProvider         (V2 — future)
├── OpenAIProvider         (future)
└── OllamaProvider         (future)

IVectorStoreProvider
├── MongoVectorStore       (V1 — current)
├── QdrantVectorStore      (future)
└── PineconeVectorStore    (future)
```
