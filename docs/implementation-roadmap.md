# IncidentIQ — Implementation Roadmap

## Phase 0 — Infrastructure Setup (Day 1)

- [ ] MongoDB Atlas cluster creation
- [ ] Vector Search index creation (see Development Guide)
- [ ] Groq API key setup
- [ ] `.env` configuration
- [ ] Verify `uvicorn main:app` starts cleanly
- [ ] Verify `npm run dev` starts cleanly

## Phase 1 — Document Upload + Processing (Days 2–4)

**Backend:**
- [ ] `POST /api/v1/documents` — file upload endpoint
- [ ] `DocumentIngestionPipeline.run()` — extract → chunk → embed → index
- [ ] `GET /api/v1/documents/{id}/stream` — SSE progress stream
- [ ] `GET /api/v1/documents` — list documents

**Frontend:**
- [ ] `UploadForm` — drag-drop with file type + size validation
- [ ] `ProcessingProgress` — SSE-driven stage visualization
- [ ] `useUpload` + `useSSE` hooks wired up

**Test:** Upload a PDF → observe SSE stages → verify chunks appear in MongoDB

---

## Phase 2 — Semantic Search (Days 5–6)

**Backend:**
- [ ] `POST /api/v1/search` — vector search + RAG answer
- [ ] `SearchService.search()` — encode → vector search → rerank → RAG
- [ ] `POST /api/v1/search/similar` — find similar incidents

**Frontend:**
- [ ] `SearchBar` with example queries
- [ ] `SearchResults` with AI answer card
- [ ] `IncidentCard` with severity, root cause, services

**Test:** Search "database connection timeout" → returns relevant results with AI answer

---

## Phase 3 — AI Assistant (Day 7)

**Backend:**
- [ ] `POST /api/v1/assistant/chat` — multi-turn RAG chat
- [ ] `AIAssistantService.chat()` — build context, inject history, call LLM

**Frontend:**
- [ ] `ChatInterface` — full conversation UI
- [ ] `ChatMessage` — user/assistant bubbles
- [ ] Source citations shown below conversation
- [ ] Suggested runbooks panel

**Test:** Ask "Have we seen Redis failures?" → coherent answer with sources

---

## Phase 4 — Polish + Production Readiness (Days 8–10)

- [ ] Error handling on all API routes (proper HTTP status codes)
- [ ] Loading states on all frontend interactions
- [ ] Empty state messages (no documents, no search results)
- [ ] Document list page with status badges
- [ ] Delete document with confirmation
- [ ] `/health/ready` endpoint with MongoDB ping
- [ ] structlog JSON logging in production mode
- [ ] CORS configuration for production domain
- [ ] Docker files for deployment

---

## Deployment Checklist

### Backend → Render

1. Create a new Web Service on Render
2. Set environment variables (copy from `.env`)
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Update `ALLOWED_ORIGINS` to include the Vercel frontend URL

### Frontend → Vercel

1. Import repo to Vercel
2. Set `NEXT_PUBLIC_API_URL` to the Render backend URL
3. Deploy

### MongoDB Atlas

1. Whitelist Render's IP addresses (or use `0.0.0.0/0` for development)
2. Ensure the vector search index is created (see Development Guide)
3. Upgrade to M10+ cluster for production vector search

---

## Future Versions

### V2 — Service Dependency Visualization
- Graph view: services ↔ incidents ↔ runbooks
- D3.js or React Flow frontend component
- Aggregate `affected_services` from all incident chunks

### V3 — Incident Timeline Analytics
- Time-series chart of incidents by severity
- Recurring patterns detection
- Service health score

### V4 — AI-Generated RCA Summaries
- Auto-summarize uploaded RCA documents
- Extract root_cause, resolution, preventive_actions structured fields
- Store as Incident entity

### V5 — MCP Server
- Wire up `mcp/tools/incident_tools.py` stubs
- Expose as MCP tools: search_incidents, find_similar, get_runbook, ask_assistant
- Zero application layer changes

### V6 — Agentic Incident Investigation
- Multi-step agent: symptom → search → correlate → draft RCA
- LangGraph or similar agent framework
- Calls existing Application Services

### V7 — Slack Integration
- Slash command `/incidentiq search <query>`
- DM notifications for similar incidents
- Slack as a new Presentation Layer adapter

### V8 — JIRA Integration
- Link incidents to JIRA tickets
- Auto-attach related runbooks to JIRA issues
- Sync incident status from JIRA

### V9 — Knowledge Graph (Neo4j)
- Service → Incident → RCA → Resolution relationships
- Graph traversal for "what services are blast radius?"
- New `IGraphRepository` interface, `Neo4jRepository` implementation

### V10 — Predictive Incident Intelligence
- Trend analysis on recurring failure patterns
- Alert when similar failure conditions observed
- ML-based similarity thresholds
