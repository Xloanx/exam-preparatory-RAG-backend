# Technical Stack Document

## 1. Overview

This document defines the technology selection for the ITF Exam Preparation RAG Platform, including the AI/ML components. It supersedes and complements the PRD with concrete stack choices, provider options, and rationale.

## 2. Stack Decision Summary

| Layer | Decision | Rationale | Alternatives |
|---|---|---|---|
| Frontend | Next.js 15 (App Router) + TypeScript + React 19 + Tailwind CSS | Mature RAG app ecosystem, server components, Vercel affinity | Remix, Vite + React |
| Backend | FastAPI (Python 3.12) + Pydantic v2 + SQLAlchemy async + Alembic | First-class LLM tooling, Pydantic structured outputs, async | Django, Node/Fastify |
| Database | Prisma Postgres (managed Postgres + pgvector) | Single managed store for metadata + vectors; Prisma choice | Supabase, Neon, self-hosted PG |
| Vector store | Prisma Postgres + pgvector (default); pluggable Pinecone/Qdrant/Weaviate/Chroma/FAISS | Managed default; abstraction for learning goal | — |
| Embeddings | OpenAI `text-embedding-3-small` (default); BGE/E5/multilingual/nomic | Cost/latency; pluggable via config | — |
| Generation LLM | OpenAI GPT-4o (GPT-4o-mini for generation); pluggable Claude/Llama-via-Groq/local | Structured outputs, function calling; pluggable | — |
| Auth | Self-managed JWT (FastAPI) + Google OAuth (FastAPI) + Next.js httpOnly cookie | Avoid vendor lock-in; Google OAuth requirement | Auth0, Clerk |

## 3. Frontend

- **Framework:** Next.js 15 (App Router), React 19, TypeScript.
- **Styling:** Tailwind CSS; component library decision pending (e.g., shadcn/ui).
- **Data fetching:** React Server Components + Server Actions; TanStack Query for client-side.
- **Deployment:** Vercel.

## 4. Backend

- **Framework:** FastAPI, Python 3.12, Pydantic v2.
- **ORM:** SQLAlchemy 2.0 (async) + Alembic migrations.
- **Serving:** Uvicorn behind gunicorn/uvicorn workers; containerised on Render or Fly.io.

## 5. Data Layer and Vector Store

- **Primary store:** Prisma Postgres (managed PostgreSQL with pgvector extension).
- Entities: users, categories, documents, chunks, questions, attempts, answers, preferences.

## 6. AI and Model Layer

- **Embeddings:** `OpenAI_API_KEY` + `text-embedding-3-small` by default; configurable to BGE, E5, multilingual, nomic via environment.
- **Generation:** OpenAI `gpt-4o` by default (mini variant for question generation); structured JSON output via Pydantic.
- **Retrieval:** hybrid (vector + BM25) default; re-ranking with cross-encoder for final top-k default.

## 7. Authentication and Authorization

- FastAPI issues JWT access + refresh tokens.
- Google OAuth handled at FastAPI layer; JWT issued to client.
- Next.js stores JWT in httpOnly cookie.
- Roles: `ADMIN` / `USER`.

## 8. Infrastructure and Deployment

- Frontend: Vercel.
- Backend: Render or Fly.io (FastAPI).
- Database: Prisma Postgres.
- Object storage: S3-compatible (AWS S3 / Cloudflare R2 / Backblaze B2).
- AI: OpenAI API.

## 9. Security

- HTTPS, JWT secrets management, rate limiting, input validation, file type/size limits, CORS policy.

## 10. Observability and Monitoring

- Structured logging; LLM tracing via Langfuse (post-MVP); basic metrics in v1.

## 11. Testing and Quality

- Backend: pytest, httpx, ruff, mypy.
- Frontend: Jest + React Testing Library; Playwright for e2e (post-MVP).

## 12. Environments and Configuration

- Local, staging, production. Provider switches via environment variables (embedding model, vector store, LLM).
