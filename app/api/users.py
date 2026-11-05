from fastapi import APIRouter

router = APIRouter()


@router.get("/users/me")
async def get_me():
    return {"user": None}
