SUPPORTED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
}

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

MONGO_COLLECTION_DOCUMENTS = "documents"
MONGO_COLLECTION_CHUNKS = "chunks"
MONGO_COLLECTION_INCIDENTS = "incidents"
MONGO_COLLECTION_USERS = "users"

MAX_SEARCH_RESULTS = 20
DEFAULT_SEARCH_RESULTS = 5
MAX_SIMILAR_RESULTS = 10
DEFAULT_SIMILAR_RESULTS = 5

RAG_CONTEXT_MAX_CHUNKS = 8
RAG_CONTEXT_MAX_CHARS = 8000

SYSTEM_PROMPT = """You are IncidentIQ, an AI assistant specialized in operational knowledge and incident management.

You help engineering teams by:
- Answering questions about historical incidents
- Identifying root causes and patterns
- Recommending relevant runbooks
- Suggesting resolution steps based on past experience

Always base your answers on the provided context. If the context does not contain enough information, say so clearly.
Be concise, precise, and actionable. Use technical language appropriate for senior engineers.
"""
