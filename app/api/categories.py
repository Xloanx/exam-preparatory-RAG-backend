from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_admin
from app.models.category import Category
from app.models.user import User

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    parent_id: int | None = None
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


def _to_out(category: Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "description": category.description,
    }


@router.post("/admin/categories")
async def create_category(
    payload: CategoryCreate, admin: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)
) -> dict:
    if payload.parent_id is not None:
        parent = (
            (await session.execute(select(Category).where(Category.id == payload.parent_id))).scalar_one_or_none()
        )
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")

    category = Category(name=payload.name, parent_id=payload.parent_id, description=payload.description)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return {"category": _to_out(category), "id": category.id}


@router.get("/admin/categories")
async def list_categories(admin: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)) -> list:
    result = await session.execute(select(Category).order_by(Category.id))
    categories = result.scalars().all()
    return {"categories": [_to_out(c) for c in categories]}


@router.put("/admin/categories/{category_id}")
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    category = (
        (await session.execute(select(Category).where(Category.id == category_id))).scalar_one_or_none()
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if payload.name is not None:
        category.name = payload.name
    if payload.description is not None:
        category.description = payload.description
    await session.commit()
    return {"category": _to_out(category)}


@router.delete("/admin/categories/{category_id}")
async def delete_category(
    category_id: int, admin: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)
):
    category = (
        (await session.execute(select(Category).where(Category.id == category_id))).scalar_one_or_none()
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await session.delete(category)
    await session.commit()
    from fastapi import Response

    return Response(status_code=204)
