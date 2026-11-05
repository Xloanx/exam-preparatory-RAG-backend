# Model Design Document — ITF Exam Preparation RAG Platform

## 1. Purpose and Scope

This document defines the Retrieval-Augmented Generation (RAG) model design for the ITF Exam Preparation RAG Platform, including ingestion, chunking, embeddings, vector storage, retrieval, re-ranking, question generation, grounding, failure handling and evaluation.

## 2. Architectural Overview

The RAG system is composed of the following logical components:

1. **Ingestion Service** — handles upload, validation, OCR, extraction, classification, chunking, embedding and indexing.
2. **Chunker** — produces chunks with preserved metadata.
3. **Embedder** — converts text to vectors (OpenAI default; pluggable).
4. **Vector Store** — Prisma Postgres + pgvector default; pluggable alternatives.
5. **Retriever** — hybrid search (vector + BM25).
6. **Reranker** — cross-encoder over top-N → top-k.
7. **Question Generator** — LLM with retrieval function calling; grounded MCQs; confidence gate.
8. **Answer Generator** — grounded answer generation; citation enrichment; confidence gate/abstain.
9. **Eval Harness** — RAGAS metrics, golden set, monitoring.

## 3. Ingestion Pipeline

1. **Upload:** drag-and-drop → FastAPI → validate MIME/size → store to S3.
2. **OCR:** if scanned (no embedded text) → OCR (PaddleOCR/Tesseract).
3. **Extraction:** pypdf / python-docx / python-pptx (+ OCR fallback).
4. **Classification:** manual selection (General | specific category) at v1.
5. **Chunking:** heading-aware split preferred; recursive fallback.
6. **Embedding:** embed chunks → persist vector + metadata.
7. **Versioning:** new version → delete old chunks → re-index.

## 4. Chunking Strategy

- Heading-aware split preferred; recursive character split fallback.
- Defaults: 800–1200 chars (~200 words); overlap 10–15%.
- Metadata: source doc, section/heading, page.

## 5. Embedding and Vector Store Design

- Default: OpenAI `text-embedding-3-small` (1536 dims, cosine).
- Default store: Prisma Postgres + pgvector.
- Interfaces: `Embedder`, `VectorStore`; pluggable providers.

## 6. Retrieval Design

- Hybrid: pgvector vector + Postgres full-text BM25.
- Re-rank: cross-encoder over top-N → top-k (3–5).

## 7. Question Generation Design

- LLM GPT-4o + JSON mode + Pydantic schema.
- Retrieval function calling (retrieval tool); optional web search tool (flagged).
- Grounded MCQ generation; citations from chunk metadata.
- Confidence gate: abstain if low.

## 8. Answer Generation and Grounding

- Grounded prompt; answer quotes source; citations (doc, section, page).
- Confidence threshold before answering.

## 9. Fine-Tuning Roadmap

- Phase 3: Q-gen fine-tuning; embed drift; data export.

## 10. Failure Handling

- Retries, fallbacks, abstain, logging.

## 11. Evaluation Design

- RAGAS: faithfulness, answer relevancy, context relevancy.
- Golden set; human eval.
