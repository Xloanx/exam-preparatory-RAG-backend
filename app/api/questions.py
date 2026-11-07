import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_admin, get_db
from app.config import settings
from app.models.category import Category
from app.models.document import Document
from app.models.question import Question
from app.models.user import User

router = APIRouter()


class ExpertQuestionCreate(BaseModel):
    stem: str
    options: list[str] = Field(min_length=2)
    correct_answer: str
    explanation: str | None = None
    source: str = "EXPERT"
    category_id: int | None = None
    document_id: int | None = None


class GenerateQuestionsRequest(BaseModel):
    document_ids: list[int] = []
    category_id: int | None = None


def _question_out(q: Question) -> dict:
    return {
        "id": q.id,
        "source": q.source,
        "document_id": q.document_id,
        "chunk_id": q.chunk_id,
        "category_id": q.category_id,
        "stem": q.stem,
        "options": json.loads(q.options) if q.options else [],
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
    }


def _build_prompt(question_count: int) -> str:
    return (
        "You are an expert ITF (Industrial Training Fund) exam item writer. "
        f"Generate {question_count} multiple choice questions (A-D) with one correct answer, "
        "an explanation, and a confidence score. Return strict JSON: "
        '{"questions": [{"stem": "...", "options": ["...", ...], "correct_answer": "...", "explanation": "...", "confidence": 0.0}]}. '
        "ITF exam context: Industrial Training Fund Nigeria; assess competency in the approved curricula."
    )


@router.post("/admin/questions")
async def add_question(
    payload: ExpertQuestionCreate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    question = Question(
        source=payload.source,
        category_id=payload.category_id,
        document_id=payload.document_id,
        stem=payload.stem,
        options=json.dumps(payload.options),
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return _question_out(question)


@router.post("/admin/questions/generate")
async def generate_questions(
    payload: GenerateQuestionsRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    if not payload.document_ids and payload.category_id is None:
        raise HTTPException(status_code=422, detail="Provide document_ids or category_id")

    if payload.document_ids:
        docs = (
            (
                await session.execute(
                    select(Document).where(Document.id.in_(payload.document_ids))
                )
            )
            .scalars()
            .all()
        )
        if len(docs) != len(payload.document_ids):
            raise HTTPException(status_code=404, detail="One or more documents not found")
    else:
        category = (
            (await session.execute(select(Category).where(Category.id == payload.category_id))).scalar_one_or_none()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        docs = (
            (
                await session.execute(
                    select(Document).where(
                        Document.classification == "CATEGORY", Document.category_id == payload.category_id
                    )
                )
            )
            .scalars()
            .all()
        )

    if not docs:
        return {"questions": []}

    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503, detail="Question generation is not configured (OPENAI_API_KEY missing)"
        )

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL or "gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are an expert exam item writer for the ITF.",
            },
            {"role": "user", "content": _build_prompt(len(docs))},
        ],
    )
    content = response.choices[0].message.content
    parsed = json.loads(content)
    generated = parsed.get("questions", [])

    questions = []
    for item in generated:
        question = Question(
            source="GENERATED",
            category_id=payload.category_id if payload.category_id else None,
            document_id=docs[0].id if len(docs) == 1 else None,
            stem=item["stem"],
            options=json.dumps(item["options"]),
            correct_answer=item["correct_answer"],
            explanation=item.get("explanation"),
        )
        session.add(question)
        questions.append(question)

    await session.commit()
    for q in questions:
        await session.refresh(q)
    return {"questions": [_question_out(q) for q in questions]}
