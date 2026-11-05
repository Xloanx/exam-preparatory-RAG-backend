# App Flow Document — ITF Exam Preparation RAG Platform

## 1. Overview

Defines end-to-end application flows for admin content pipeline and user exam lifecycle.

## 2. Admin Flow

1. Bootstrap admin seeded.
2. Admin creates other admins.
3. Admin manages category hierarchy (CRUD).
4. Admin uploads documents (drag-and-drop).
5. Admin classifies documents (general vs. specific).
6. System ingests (OCR/extract/chunk/embed).
7. System generates questions from new docs.
8. Admin adds expert questions.
9. New document version replaces old (re-index).

## 3. User Flow

1. Register (email/password or Google OAuth).
2. Login → optionally change category.
3. Configure exam (scope, count, time, reshuffle).
4. Start session → RAG generation → eligibility filtering.
5. Answer → Submit → Score.
6. View Answers → correct answer + source doc + section + page.
7. Retake / history.

## 4. State Machines

- Attempt lifecycle states; category change handling; document version states.
