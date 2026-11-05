# Data Model — ITF Exam Preparation RAG Platform

## Document Control

- **Project:** ITF Exam Preparation RAG Platform
- **Version:** 1.0 (Draft)
- **Date:** 2026-11-01

---

## 1. Entity Overview

1. **User**
2. **Category**
3. **Document**
4. **Chunk**
5. **Question**
6. **Attempt**
7. **UserPreference**

## 2. Entities

### User
- id, email, password_hash, auth_provider, full_name, current_category_id, roles[], preferences, created_at, updated_at.

### Category
- id, name, parent_id (nullable → hierarchy), description, cadre/level metadata, is_active.

### Document
- id, filename, s3_key, classification (`GENERAL` | `CATEGORY`), category_id, status (`UPLOADED | CLASSIFIED | INGESTING | INDEXED | FAILED`), version metadata, timestamps.

### Chunk
- id, document_id, content, source_doc, section/heading, page, char_start, char_end, token_count, embedding (vector), metadata.

### Question
- id, source (`GENERATED` | `EXPERT`), document_id/chunk_id, category_id, stem, options[], correct_answer, explanation, confidence, generation metadata, timestamps.

### Attempt
- id, user_id, exam_config snapshot, answers[], score, started_at, submitted_at.

### UserPreference
- user_id, scopes[], question_count, time_limit_minutes?, reshuffle, updated_at.

## 3. Vector Storage

- Prisma Postgres + pgvector; embedding dimension per provider (e.g., 1536 for text-embedding-3-small).

## 4. Relationships

- User → Category (current).
- Document → Category.
- Chunk → Document.
- Question → Chunk/Document/Category.
- Attempt → User.
- UserPreference → User.

## 5. Invariants

- New document versions replace old (delete/re-index).
- Attempt history preserved across category changes.

---

## 6. Access Control Rules

- Admin endpoints require `ADMIN` role.
- Users manage own profile/preferences.
- Question eligibility: General + own/sub-categories.
