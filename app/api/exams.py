from fastapi import APIRouter

router = APIRouter()


@router.post("/exams/sessions")
async def start_session():
    return {"ok": True}
