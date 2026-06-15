# ADR-001: Clean Architecture

**Status:** Accepted
**Date:** 2024-01-01

## Context

IncidentIQ needs to support future integrations (MCP, Slack, JIRA, Knowledge Graph) without rewriting core business logic. We need to choose a structural pattern that keeps the system extensible.

## Decision

Adopt Clean Architecture with four layers: Presentation, Application, Domain, Infrastructure. All dependencies point inward — nothing in Domain or Application may import from FastAPI, MongoDB, or Groq.

## Consequences

**Positive:**
- Swapping MongoDB for Qdrant requires only a new infrastructure class, not touching services
- Adding a Slack interface requires only a new presentation adapter
- Domain logic is unit-testable without any external services
- MCP tools can call Application Services directly

**Negative:**
- More files than a simple CRUD structure
- Developers must learn the dependency rule

## Enforcement

- Domain layer has zero third-party imports
- Application layer may only import from domain
- Infrastructure implements domain repository interfaces
- Routes may only import from application DTOs and services
