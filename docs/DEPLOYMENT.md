# Deployment Guide — ITF Exam Preparation RAG Platform

## Document Control

- **Project:** ITF Exam Preparation RAG Platform
- **Version:** 1.0 (Draft)
- **Date:** 2026-11-01

---

## 1. Architecture Overview

```
Browser (Next.js on Vercel)
   → FastAPI (Render/Fly.io)
        → Prisma Postgres (pgvector)
        → S3 (documents)
        → OpenAI (embeddings + LLM)
```

## 2. Components

1. **Frontend:** Next.js 15 App Router → Vercel.
2. **Backend:** FastAPI → Render or Fly.io.
3. **Database:** Prisma Postgres (pgvector).
4. **Storage:** S3-compatible.
5. **AI:** OpenAI.

## 3. Environments

- Local, Staging, Production.

## 4. Environment Variables

- `OPENAI_API_KEY`, `EMBEDDING_MODEL`, `VECTOR_STORE`, `LLM_MODEL`, `JWT_SECRET`, `DATABASE_URL`, `S3_*`, `NEXT_PUBLIC_*`.

## 5. CI/CD

- GitHub Actions for backend/frontend pipelines.

## 6. Rollback / Launch Checklist

- Seed admin; create categories; upload docs; generate Qs; onboard users.

## 7. Monitoring

- Structured logs; Langfuse (post-MVP).
