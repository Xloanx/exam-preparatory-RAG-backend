from fastapi import APIRouter

router = APIRouter()


@router.post("/admin/questions/generate")
async def generate_questions():
    return {"ok": True}
