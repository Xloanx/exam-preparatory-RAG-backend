from fastapi import APIRouter

from app import db

router = APIRouter()


@router.post("/auth/register")
async def register():
    return {"ok": True}
