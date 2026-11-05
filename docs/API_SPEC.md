# API Specification — ITF Exam Preparation RAG Platform

## Document Control

- **Project:** ITF Exam Preparation RAG Platform
- **Version:** 1.0 (Draft)
- **Date:** 2026-11-01

---

## 1. Overview

REST API for the ITF Exam Preparation RAG Platform, versioned under `/api/v1`. Consumes and produces JSON. JWT-based authentication.

## 2. Conventions

- Base URL: `/api/v1`
- Auth: Bearer JWT (access token). Refresh token rotation.
- Content-Type: `application/json` for JSON bodies; multipart for file uploads.

## 3. Authentication Endpoints

### POST `/auth/register`
- **Body:** `{ email, password, full_name }`
- **Response:** `201 Created` — user object (no password).

### POST `/auth/login`
- **Body:** `{ email, password }`
- **Response:** `200 OK` — `{ access_token, refresh_token, user }`

### POST `/auth/google` (OAuth callback → issue JWT)
- Handles Google OAuth token exchange; issues ITF JWT.

### POST `/auth/refresh`
- **Body:** `{ refresh_token }`
- **Response:** `200 OK` — new access token.

### POST `/auth/logout`
- Revokes refresh token.

## 4. Admin Endpoints

### Categories
- `POST /admin/categories` — create category `{ name, parent_id?, description? }`
- `GET /admin/categories` — list hierarchy
- `PUT /admin/categories/{id}` — update
- `DELETE /admin/categories/{id}` — deactivate/delete

### Documents
- `POST /admin/documents/upload` — multipart upload `{ file }` → returns doc `{ id, filename, status }`
- `POST /admin/documents/{id}/classify` — `{ classification: "GENERAL" | "CATEGORY", category_id? }`
- `POST /admin/documents/{id}/ingest` — trigger ingestion (OCR → extract → chunk → embed → index)

### Questions
- `POST /admin/questions/generate` — `{ document_ids[] }` or `{ category_id }` → generate MCQs via LLM
- `POST /admin/questions` — add expert question `{ stem, options[], correct_answer, explanation, category_id }`

## 5. User Endpoints

### Profile
- `GET /users/me` — current user incl. current category, preferences
- `PUT /users/me/category` — `{ category_id }` (change at login)

### Exam Configuration
- `PUT /users/me/exam-preferences` — `{ scopes: ["GENERAL"|"CAT_x"], question_count, time_limit_minutes?, reshuffle? }`

### Exam Sessions
- `POST /exams/sessions` — start session `{ exam_preferences }` → returns session `{ id, questions[] }`
- `GET /exams/sessions/{id}` — session status + questions
- `POST /exams/sessions/{id}/answers` — submit answers `{ answers: [{ question_id, selected_option_index }] }`
- `GET /exams/sessions/{id}/answers` — view answers + citations (correct answer + source doc + section + page)

## 6. Evaluation Endpoints

- `POST /eval/run` — trigger RAGAS evaluation (retrieval, faithfulness, answer relevancy).

---

## 7. Error Handling

- Standard error envelope: `{ error: { code, message, details? } }`
- Auth errors: `401`; validation: `422`; not found: `404`.
