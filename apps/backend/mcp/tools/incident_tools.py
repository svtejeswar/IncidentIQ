"""
MCP Tool stubs for IncidentIQ — V5 future implementation.

These interfaces define the contract for MCP tools that will be exposed
when MCP Server integration is built. They delegate directly to Application
Services with zero business logic here.

When building MCP V5:
1. Install an MCP Python SDK
2. Wrap these functions as MCP tool handlers
3. Wire up the same Application Service instances via DI
4. Zero changes needed to domain or application layer
"""
from __future__ import annotations

from uuid import UUID


async def search_incidents(query: str, limit: int = 5) -> dict:
    """
    MCP tool: Search historical incidents using natural language.

    Future implementation will call:
        search_service.search(SearchRequest(query=query, limit=limit))
    """
    raise NotImplementedError("MCP integration pending V5")


async def find_similar_incidents(document_id: str | None = None, text: str | None = None) -> dict:
    """
    MCP tool: Find incidents similar to a given document or description.

    Future implementation will call:
        search_service.find_similar(document_id=UUID(document_id), text=text)
    """
    raise NotImplementedError("MCP integration pending V5")


async def get_runbook(query: str) -> dict:
    """
    MCP tool: Retrieve a relevant runbook for the given incident description.

    Future implementation will call:
        search_service.search(SearchRequest(query=query, document_types=[DocumentType.RUNBOOK]))
    """
    raise NotImplementedError("MCP integration pending V5")


async def ask_incident_assistant(message: str, conversation_id: str | None = None) -> dict:
    """
    MCP tool: Ask the AI assistant a question about operational knowledge.

    Future implementation will call:
        assistant_service.chat(ChatRequest(message=message, conversation_id=conversation_id))
    """
    raise NotImplementedError("MCP integration pending V5")
