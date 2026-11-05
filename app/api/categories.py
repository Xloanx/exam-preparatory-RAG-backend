from fastapi import APIRouter

router = APIRouter()


@router.post("/admin/categories")
async def create_category():
    return {"ok": True}
