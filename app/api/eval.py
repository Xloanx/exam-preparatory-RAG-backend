from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_admin, get_db
from app.models.attempt import Attempt
from app.models.user import User

router = APIRouter()


@router.post("/eval/run")
async def run_eval(admin: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)) -> dict:
    # Phase 1: eval endpoint scaffold. RAGAS metrics wiring lands in Phase 2
    # once retrieval (embeddings + vector search) and OpenAI generation are enabled.
    result = await session.execute(select(Attempt).limit(1))
    sample_attempts = result.scalars().all()
    return {
        "status": "ok",
        "message": "RAGAS evaluation wiring is planned for Phase 2 (retrieval + OpenAI).",
        "attempts_sampled": len(sample_attempts),
    }
