from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/admin/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    return {"ok": True}
