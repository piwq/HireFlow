from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.deps import get_current_user
from app.models.user import User
from app.services.s3 import upload_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    allowed_types = (
        "application/pdf", 
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/webp"
    )
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed. Supported: PDF, Word, JPG, PNG, WEBP")

    # Валидация размера файла (10 МБ)
    MAX_SIZE = 10 * 1024 * 1024
    # Starlette/FastAPI UploadFile.size может быть None в старых версиях
    size = getattr(file, "size", None)
    if size is None:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
    
    if size > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"Файл слишком большой ({size / 1024 / 1024:.1f} МБ). Максимум: 10 МБ")

    url = await upload_file(file)
    return {"url": url}
