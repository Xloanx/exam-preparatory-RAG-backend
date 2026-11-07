from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.api.auth import get_current_admin, get_db
from app.models.category import Category
from app.models.document import Document
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = Path("uploads")


class ClassifyRequest(BaseModel):
    classification: str  # "GENERAL" | "CATEGORY"
    category_id: int | None = None


def _to_out(doc: Document) -> dict:
    return {
        "id": doc.id,
        "filename": doc.filename,
        "s3_key": doc.s3_key,
        "classification": doc.classification,
        "category_id": doc.category_id,
        "status": doc.status,
    }


@router.post("/admin/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    contents = await file.read()
    dest = UPLOAD_DIR / file.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(contents)

    doc = Document(filename=file.filename, status="UPLOADED", classification="GENERAL", category_id=None)
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return _to_out(doc)


@router.post("/admin/documents/{document_id}/classify")
async def classify_document(
    document_id: int,
    payload: ClassifyRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    doc = (
        (await session.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if payload.classification not in ("GENERAL", "CATEGORY"):
        raise HTTPException(status_code=422, detail="classification must be GENERAL or CATEGORY")

    doc.classification = payload.classification
    doc.category_id = payload.category_id if payload.classification == "CATEGORY" else None
    await session.commit()
    return _to_out(doc)


@router.post("/admin/documents/{document_id}/ingest")
async def ingest_document(
    document_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    doc = (
        (await session.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = "INDEXED"
    await session.commit()
    return _to_out(doc)
