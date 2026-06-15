# ADR-004: MongoDB Atlas Vector Search

**Status:** Accepted
**Date:** 2024-01-01

## Context

We need a vector store for semantic search. Options: dedicated vector DB (Qdrant, Pinecone), or MongoDB Atlas Vector Search (our existing DB).

## Decision

Use MongoDB Atlas Vector Search for V1. Store chunks + embeddings in the `chunks` collection. Use `$vectorSearch` aggregation pipeline for ANN (approximate nearest neighbor) search.

## Rationale

| Factor | MongoDB Atlas | Qdrant/Pinecone |
|---|---|---|
| Infrastructure complexity | One system (no extra service) | Two separate services |
| V1 scale (< 1M vectors) | Fully sufficient | Overkill |
| Team familiarity | MongoDB already chosen | New system to learn |
| Cost | Included in Atlas | Additional cost |
| Migration path | Easy via `IVectorStoreProvider` | Easy via same interface |

For V1 scale (thousands to low millions of chunks), Atlas Vector Search performs well. The `IVectorStoreProvider` interface ensures we can migrate to Qdrant in V5+ without touching business logic.

## Index Configuration

```json
{
  "fields": [{
    "type": "vector",
    "path": "embedding",
    "numDimensions": 384,
    "similarity": "cosine"
  }]
}
```

Cosine similarity chosen because `all-MiniLM-L6-v2` embeddings are normalized — cosine and dot-product are equivalent, but cosine is more intuitive.

## Consequences

**Positive:**
- Single Atlas cluster for both document metadata and vectors
- No additional infrastructure in local development
- Familiar MongoDB query patterns for filtering by document_type, severity, etc.

**Negative:**
- Atlas Vector Search requires M10+ cluster for production (not free tier)
- Not as feature-rich as dedicated vector DBs for complex filtering
- Must be replaced if we need hybrid search or BM25 scoring

## Migration Path

When replacing with Qdrant: implement `QdrantVectorStore(IVectorStoreProvider)`, update `providers.py`. Zero other changes needed.
