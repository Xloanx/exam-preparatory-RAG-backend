# Decision Log — ITF Exam Preparation RAG Platform

## Document Control

- **Project:** ITF Exam Preparation RAG Platform
- **Version:** 1.0 (Draft)
- **Date:** 2026-11-01

---

## 1. Key Decisions

1. **Vector store:** Prisma Postgres + pgvector (default); pluggable Pinecone/Qdrant/Weaviate/Chroma/FAISS.
2. **Embeddings:** OpenAI `text-embedding-3-small` (default); pluggable BGE/E5/multilingual/nomic.
3. **LLM:** GPT-4o (GPT-4o-mini for generation); pluggable Claude/Llama-via-Groq/local.
4. **Hybrid search:** ON for v1 (vector + BM25).
5. **Re-ranking:** ON for v1 (cross-encoder; top-k 3–5).
6. **Fine-tuning:** Phase 3+.
7. **Failure handling:** Retries, fallbacks, abstain, logging.
8. **Grounding:** Quote source, citations, confidence threshold/abstain.

## 2. Open Items

- Multi-tenant isolation (post-MVP).
- Adaptive difficulty (post-MVP).
- Graph RAG (post-MVP).
- Fine-tuning specifics (post-MVP).

## 3. Decisions Pending User Confirmation

- Multi-select MCQ scoring semantics (exact match vs partial credit).
- OCR engine (PaddleOCR vs Tesseract).
- Time limit default behavior.

---

## 4. Decision Drivers

- Learning objectives (function calling, embeddings, fine-tuning, chunking, vectors, hybrid, re-rank, graph RAG, grounding, RAG eval).
- Organizational constraints (gov agency, compliance, ~4,000 staff).
- Delivery preferences (Vercel, Prisma Postgres, separate repos).
