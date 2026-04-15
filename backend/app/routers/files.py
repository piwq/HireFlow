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
    if file.content_type not in ("application/pdf", "application/msword",
                                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
        raise HTTPException(status_code=400, detail="Only PDF and Word files allowed")

    url = await upload_file(file)
    return {"url": url}
