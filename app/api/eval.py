from fastapi import APIRouter

router = APIRouter()


@router.post("/eval/run")
async def run_eval():
    return {"ok": True}
