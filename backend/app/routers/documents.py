from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.s3 import upload_file

router = APIRouter(prefix="/documents", tags=["documents"])

DOC_TYPES = {"resume", "cover_letter", "certificate", "diploma", "other"}

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
}


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="other"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, Word, JPG, PNG allowed")

    if doc_type not in DOC_TYPES:
        doc_type = "other"

    profile_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your profile first")

    url = await upload_file(file)

    doc = Document(
        candidate_id=profile.id,
        doc_type=doc_type,
        name=file.filename or doc_type,
        url=url,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/my", response_model=list[DocumentResponse])
async def my_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    profile_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()
    if not profile:
        return []
    result = await db.execute(
        select(Document).where(Document.candidate_id == profile.id)
    )
    return result.scalars().all()


@router.get("/candidate/{candidate_id}", response_model=list[DocumentResponse])
async def candidate_documents(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(
        select(Document).where(Document.candidate_id == candidate_id)
    )
    return result.scalars().all()


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    profile_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=403, detail="Forbidden")

    doc_res = await db.execute(
        select(Document).where(Document.id == doc_id, Document.candidate_id == profile.id)
    )
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(doc)
    await db.commit()
