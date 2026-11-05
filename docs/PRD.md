# Product Requirements Document (PRD)

## Document Control

- **Project:** ITF Exam Preparation RAG Platform
- **Version:** 1.0 (Draft for stakeholder review)
- **Date:** 2026-11-01
- **Client Context:** Industrial Training Fund (ITF), Nigeria

---

## 1. Executive Summary

The Industrial Training Fund (ITF) is a Nigerian government-owned agency under the Federal Ministry of Industry, Trade and Investment (FMITI), mandated for capacity building, manpower development and skills development. It supports approximately **4,000 staff**, of whom an average of **~1,300 write examinations each year** — principally promotion examinations into the next cadre, supplemented by general knowledge-retention assessments.

Official content is maintained in **PDF, Word and PowerPoint** documents, all in English, including **scanned documents**. Question development to date has been predominantly manual and does not scale with content volume or policy-change velocity.

This PRD specifies a **Retrieval-Augmented Generation (RAG) powered exam preparation platform** that:

1. Enables **admins** to upload, classify, ingest and manage documents; generate exam-graded **multiple choice questions (MCQs)** from content via LLM; and add **expert-authored questions**.
2. Enables **users** to register (email/password or Google OAuth), hold a single category at a time (changeable at login), configure exam preferences, sit for **retrieval-grounded MCQ sessions** (50 questions default, user-configurable), receive instant scoring, and review answers with full source citations.

The platform is also designed as a deliberate **learning platform** for modern RAG techniques — function calling, embeddings, fine-tuning, failure handling, chunking, vectors, hybrid search, re-ranking, graph RAG, grounding, and RAG evaluation (RAGAS).

## 2. Background and Context

The ITF mandate creates a recurring need for:

- **Promotion examinations:** validating knowledge for progression through the cadre ladder (e.g., TDO-III → Senior TDO, Senior TDO → Principal TDO, … Chief TDO → Assistant Director (Training), etc.).
- **General knowledge-retention assessments.**

Key facts established during discovery:

- Staff population: ~4,000; examinations: ~1,300/year average.
- Content formats: PDF, Word, PowerPoint; English; some scanned.
- Admin onboarding: first admin seeded via bootstrap script; first admin creates subsequent admins.
- Category model: hierarchical (Training Development cadre ladder; Accounting; Human Resources).
- Question source: predominantly LLM generation from document chunks, supplemented by occasional expert-authored questions.
- Ingestion: new document versions replace prior versions (policy changes).

Pain points motivating the product:

- Manual question authoring bottleneck.
- Lack of provenance / auditability for exam content.
- Hallucination risk without grounding.
- No scalable self-service preparation experience.

## 3. Goals and Non-Goals

### 3.1 Goals

- **G1:** Generate exam-viable MCQs grounded in official documents.
- **G2:** Ensure answerability and traceability (source document, section, page).
- **G3:** Deliver configurable user exam experience (scope, question count, timing, reshuffle).
- **G4:** Adopt modern RAG techniques as first-class product capabilities.

### 3.2 Non-Goals (v1)

- Adaptive difficulty engine.
- Offline / local inference deployment.
- Multi-tenant / multi-organization isolation.

## 4. Users and Roles

### 4.1 Administrator

- Seeded via bootstrap; can create other admins.
- Manages category hierarchy.
- Uploads and classifies documents.
- Triggers ingestion, question generation, expert curation.

### 4.2 Exam User (Staff)

- Open registration (email/password or Google OAuth).
- Holds exactly one category at a time; may change it at login.
- Attempt history preserved irrespective of category changes.

## 5. Functional Requirements

### FR-001: Admin Account Provisioning (P0)

**Description:** Bootstrap admin seeded; admin-created admins.

**Acceptance Criteria:**

- First admin can be seeded via CLI/bootstrap script with initial credentials.
- Seeded admin can create, suspend or remove other admins.
- Admin lifecycle actions audited.

### FR-002: Category Management (P0)

**Description:** Hierarchical categories (e.g., Training Development → cadre sub-levels; Accounting; HR).

**Acceptance Criteria:**

- Admin can create, edit and deactivate categories.
- Parent/child hierarchy supported.

### FR-003: Document Upload and Classification (P0)

**Description:** Drag-and-drop upload; manual classification.

**Acceptance Criteria:**

- Drag-and-drop with file-type allowlist (PDF, DOCX, PPTX, TXT) and size cap.
- Manual classification at v1: *General* or a specific category.

### FR-004: Ingestion, Chunking and Indexing (P0)

**Description:** OCR, extraction, chunking, embedding, indexing with metadata; version replacement.

**Acceptance Criteria:**

- OCR for scanned documents before text extraction.
- Metadata: doc name, section, page.
- New versions replace prior versions (delete/re-index).

### FR-005: LLM Question Generation (P0)

**Description:** MCQs from chunks; grounding; citations; confidence gating.

**Acceptance Criteria:**

- Generate MCQs (single-select, multi-select, true/false) from retrieved chunks.
- Grounded generation with citations; confidence gating before accepting a question.

### FR-006: Expert Question Curation (P1)

- Admin can add expert-authored questions to the bank.

### FR-007: User Registration and Login (P0)

- Open registration: email/password or Google OAuth.

### FR-008: User Category Assignment / Change (P0)

- User holds one category at a time; changeable at login.
- Attempt history preserved across category changes.

### FR-009: Exam Configuration (P0)

- Scope: General / specific category / mixed.
- Question count: default 50, user-configurable.
- Time limit: optional, user-configurable.
- Reshuffle: per-attempt / new questions.

### FR-010: Question Eligibility (P0)

- General category exposed to all.
- Within a category, user at higher sub-category sees questions from own and sub-categories below within same category.

### FR-011: Session Question Generation (P0)

- Generate session questions via RAG; distinct questions per attempt.

### FR-012: Answer Submission and Scoring (P0)

- Score at submission; no pass/fail threshold.

### FR-013: Answer Review and Source Citation (P0)

- Display: correct answer + source document + section/heading + page number (if available).
- Answers grounded/quoted from source chunks with confidence threshold before answering.

### FR-014: Retakes and Attempt History (P0)

## 6. Data and Content Model

- **User:** identity, auth provider, current category, roles, preferences, audit trail.
- **Category:** name, parent (nullable → hierarchy), description, cadre/level metadata.
- **Document:** filename, storage key, classification (general vs. specific), category, version semantics, status.
- **Chunk:** content, source document, section/heading, page, offsets, embedding, token count.
- **Question:** source (generated | expert), originating chunk/document, category scope, stem, options, correct answer, explanation, confidence, generation metadata.
- **Attempt:** user, exam config snapshot, answers, score, timestamps.

## 7. Non-Functional Requirements

- Performance: first-question latency targets; submission feedback targets.
- Security & compliance: gov-adjacent sensitivity → RBAC, audit logging, data protection.
- Reliability: graceful degradation, retries, abstain behaviour.

## 8. Assumptions and Constraints

- Single organization initially (multi-tenant deferred).
- Managed cloud services preferred (Vercel, Prisma Postgres, S3).
- English-only content at launch.

## 9. Success Metrics

- Question generation throughput and quality.
- RAG groundedness (RAGAS faithfulness).
- Retrieval relevance.
- User completion and retake rates.

## 10. Decision Log and Open Items

- Vector store default: Prisma Postgres + pgvector; pluggable alternatives.
- Embeddings default: OpenAI `text-embedding-3-small`; pluggable open-source models.
- LLM default: OpenAI GPT-4o; pluggable.
- Hybrid search, re-ranking, fine-tuning scope: decisions documented in the Technical Design Document.
