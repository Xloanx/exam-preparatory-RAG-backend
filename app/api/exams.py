import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_user, get_db
from app.models.attempt import Attempt
from app.models.category import Category
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.question import Question
from app.models.user import User

router = APIRouter()

GENERAL_SCOPE = "GENERAL"
DEFAULT_QUESTION_COUNT = 50
MAX_QUESTION_COUNT = 200


class ExamPreferences(BaseModel):
    scopes: list[str] = [GENERAL_SCOPE]
    question_count: int = DEFAULT_QUESTION_COUNT
    time_limit_minutes: int | None = 30
    reshuffle: bool = False


class AnswerItem(BaseModel):
    question_id: int
    selected_option_index: int


class AnswerSubmitRequest(BaseModel):
    answers: list[AnswerItem]


def _parse_scopes(scopes: list[str]) -> tuple[list[int | None], list[str]]:
    """Returns (general_or_specific category ids, scope labels). None category id == general scope."""
    general: list[int | None] = []
    specific: list[int] = []
    labels: list[str] = []
    for scope in scopes or [GENERAL_SCOPE]:
        if scope == GENERAL_SCOPE or scope == "GENERAL":
            if None not in general:
                general.append(None)
            labels.append(GENERAL_SCOPE)
        else:
            cat_id = int(str(scope).split("_", 1)[1]) if str(scope).upper().startswith("CAT_") else int(scope)
            if cat_id not in specific:
                specific.append(cat_id)
            labels.append(f"CAT_{cat_id}")
    return general, specific, labels


def _descendant_ids(categories: list[Category], root_id: int) -> set[int]:
    children_map: dict[int | None, list[int]] = {}
    for c in categories:
        children_map.setdefault(c.parent_id, []).append(c.id)
    descendants = {root_id}
    stack = [root_id]
    while stack:
        current = stack.pop()
        for child in children_map.get(current, []):
            if child not in descendants:
                descendants.add(child)
                stack.append(child)
    return descendants


async def _question_with_citation(q: Question, session: AsyncSession) -> dict:
    source_doc = None
    section = None
    page = None
    if q.chunk_id:
        chunk = await session.get(Chunk, q.chunk_id)
        if chunk:
            source_doc = chunk.source_doc
            section = chunk.section
            page = chunk.page
    if not source_doc and q.document_id:
        doc = await session.get(Document, q.document_id)
        if doc:
            source_doc = doc.filename
    return {
        "id": q.id,
        "source": q.source,
        "category_id": q.category_id,
        "stem": q.stem,
        "options": json.loads(q.options) if q.options else [],
        "explanation": q.explanation,
        "source_doc": source_doc,
        "section": section,
        "page": page,
    }


@router.post("/exams/sessions")
async def start_exam_session(
    preferences: ExamPreferences,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    general_ids, specific_ids, labels = _parse_scopes(preferences.scopes)

    if user.current_category_id is None and specific_ids:
        raise HTTPException(status_code=403, detail="No category selected; only the general scope is allowed")

    all_categories = (await session.execute(select(Category))).scalars().all()
    allowed: set[int | None] = set(general_ids)
    for cat_id in specific_ids:
        if user.current_category_id is None:
            raise HTTPException(status_code=403, detail="No category selected; only the general scope is allowed")
        descendants = _descendant_ids(all_categories, user.current_category_id)
        if cat_id not in descendants:
            raise HTTPException(status_code=403, detail="Requested category is outside the user's eligible scope")
        allowed.add(cat_id)

    question_count = max(1, min(preferences.question_count, MAX_QUESTION_COUNT))

    questions: list[Question] = []
    for cat_id in sorted({cid for cid in allowed if cid is not None}, key=lambda cid: cid):
        result = await session.execute(select(Question).where(Question.category_id == cat_id).order_by(Question.id))
        questions.extend(result.scalars().all())
    if None in allowed:
        result = await session.execute(select(Question).where(Question.category_id == None).order_by(Question.id))
        questions.extend(result.scalars().all())

    if preferences.reshuffle and len(questions) > 1:
        import random

        random.shuffle(questions)

    questions = questions[:question_count]

    attempt = Attempt(
        user_id=user.id,
        exam_config=json.dumps(
            {
                "scopes": preferences.scopes,
                "question_count": question_count,
                "time_limit_minutes": preferences.time_limit_minutes,
                "reshuffle": preferences.reshuffle,
            }
        ),
        answers=None,
        score=None,
    )
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)

    question_dicts = [await _question_with_citation(q, session) for q in questions]
    return {
        "attempt_id": attempt.id,
        "exam_config": json.loads(attempt.exam_config),
        "questions": question_dicts,
    }


@router.get("/exams/sessions/{session_id}")
async def get_exam_session(
    session_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    attempt = (
        (await session.execute(select(Attempt).where(Attempt.id == session_id, Attempt.user_id == user.id)))
        .scalars()
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam session not found")

    questions: list[Question] = []
    if attempt.exam_config:
        config = json.loads(attempt.exam_config)
        category_ids = [
            None if s == GENERAL_SCOPE or s == "GENERAL" else int(str(s).split("_", 1)[1])
            for s in config.get("scopes", [])
        ]
        for cat_id in sorted({cid for cid in category_ids if cid is not None}):
            result = await session.execute(
                select(Question).where(Question.category_id == cat_id).order_by(Question.id)
            )
            questions.extend(result.scalars().all())
        if None in category_ids:
            result = await session.execute(
                select(Question).where(Question.category_id == None).order_by(Question.id)
            )
            questions.extend(result.scalars().all())

    question_dicts = [await _question_with_citation(q, session) for q in questions]
    return {
        "attempt_id": attempt.id,
        "exam_config": json.loads(attempt.exam_config),
        "questions": question_dicts,
    }


@router.post("/exams/sessions/{session_id}/answers")
async def submit_answers(
    session_id: int,
    payload: AnswerSubmitRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    attempt = (
        (await session.execute(select(Attempt).where(Attempt.id == session_id, Attempt.user_id == user.id)))
        .scalars()
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam session not found")

    stored: dict[int, dict] = {}
    if attempt.answers:
        for a in json.loads(attempt.answers):
            stored[a["question_id"]] = a

    correct_count = 0
    details: list[dict] = []
    for answer in payload.answers:
        question = (await session.execute(select(Question).where(Question.id == answer.question_id))).scalars().first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        options = json.loads(question.options) if question.options else []
        selected_text = (
            options[answer.selected_option_index] if answer.selected_option_index < len(options) else None
        )
        is_correct = bool(
            selected_text
            and question.correct_answer
            and selected_text.strip().lower() == question.correct_answer.strip().lower()
        )
        if is_correct:
            correct_count += 1
        stored[answer.question_id] = {
            "question_id": answer.question_id,
            "selected_option_index": answer.selected_option_index,
            "selected_option": selected_text,
            "correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
        }
        details.append(stored[answer.question_id])

    total = len(payload.answers)
    score = round((correct_count / total) * 100, 2) if total else 0.0

    attempt.answers = json.dumps(list(stored.values()))
    attempt.score = int(score) if total else None
    await session.commit()

    return {"attempt_id": attempt.id, "score": score, "correct": correct_count, "total": total}


@router.get("/exams/sessions/{session_id}/answers")
async def view_answers(
    session_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    attempt = (
        (await session.execute(select(Attempt).where(Attempt.id == session_id, Attempt.user_id == user.id)))
        .scalars()
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam session not found")

    answers = json.loads(attempt.answers) if attempt.answers else []
    details = []
    for stored in answers:
        question = (await session.execute(select(Question).where(Question.id == stored["question_id"]))).scalars().first()
        if not question:
            continue
        options = json.loads(question.options) if question.options else []
        selected_text = (
            options[stored.get("selected_option_index") or 0] if stored.get("selected_option_index", 0) < len(options) else None
        )
        citation = await _question_with_citation(question, session)
        details.append(
            {
                "question_id": question.id,
                "selected_option_index": stored.get("selected_option_index"),
                "selected_option": stored.get("selected_option") or selected_text,
                "correct": stored.get("correct", False),
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "source_doc": citation.get("source_doc"),
                "section": citation.get("section"),
                "page": citation.get("page"),
            }
        )

    return {"attempt_id": attempt.id, "score": attempt.score, "answers": details}
