from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_user, get_db
from app.models.category import Category
from app.models.user import User

router = APIRouter()


async def _get_user_or_404(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/users/me")
async def get_me(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> dict:
    category = None
    if user.current_category_id:
        result = await session.execute(
            select(Category).where(Category.id == user.current_category_id)
        )
        category = result.scalar_one_or_none()

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "current_category_id": user.current_category_id,
            "roles": user.roles,
            "current_category": (
                {"id": category.id, "name": category.name, "description": category.description}
                if category
                else None
            ),
        }
    }


class ChangeCategoryRequest(BaseModel):
    category_id: int


@router.put("/users/me/category")
async def change_category(
    payload: ChangeCategoryRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    category = (
        (await session.execute(select(Category).where(Category.id == payload.category_id))).scalar_one_or_none()
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    user.current_category_id = payload.category_id
    await session.commit()

    fresh = await _get_user_or_404(session, user.id)
    return {"user": {"id": fresh.id, "email": fresh.email, "full_name": fresh.full_name}}
