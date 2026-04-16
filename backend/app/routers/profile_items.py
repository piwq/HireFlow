"""CRUD endpoints for structured candidate profile items (work experience, education, languages, projects)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.work_experience import WorkExperience
from app.models.education import Education
from app.models.language import Language
from app.models.project import ProjectCertificate
from app.schemas.profile_items import (
    WorkExperienceCreate, WorkExperienceResponse,
    EducationCreate, EducationResponse,
    LanguageCreate, LanguageResponse,
    ProjectCertificateCreate, ProjectCertificateResponse,
)

router = APIRouter(prefix="/profile-items", tags=["profile-items"])


async def _get_candidate_id(user: User, db: AsyncSession) -> int:
    res = await db.execute(
        select(CandidateProfile.id).where(CandidateProfile.user_id == user.id)
    )
    cid = res.scalar_one_or_none()
    if not cid:
        raise HTTPException(status_code=400, detail="Complete your profile first")
    return cid


# ── Work Experience ──────────────────────────────────────
@router.post("/work-experience", response_model=WorkExperienceResponse, status_code=201)
async def add_work_experience(
    body: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    item = WorkExperience(candidate_id=cid, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/work-experience", response_model=list[WorkExperienceResponse])
async def list_work_experience(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(WorkExperience).where(WorkExperience.candidate_id == cid))
    return res.scalars().all()


@router.get("/work-experience/candidate/{candidate_id}", response_model=list[WorkExperienceResponse])
async def list_work_experience_for_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    res = await db.execute(select(WorkExperience).where(WorkExperience.candidate_id == candidate_id))
    return res.scalars().all()


@router.delete("/work-experience/{item_id}", status_code=204)
async def delete_work_experience(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(WorkExperience).where(WorkExperience.id == item_id, WorkExperience.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    await db.commit()


@router.put("/work-experience/{item_id}", response_model=WorkExperienceResponse)
async def update_work_experience(
    item_id: int,
    body: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(WorkExperience).where(WorkExperience.id == item_id, WorkExperience.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    for field, value in body.model_dump().items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item


# ── Education ────────────────────────────────────────────
@router.post("/education", response_model=EducationResponse, status_code=201)
async def add_education(
    body: EducationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    item = Education(candidate_id=cid, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/education", response_model=list[EducationResponse])
async def list_education(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Education).where(Education.candidate_id == cid))
    return res.scalars().all()


@router.get("/education/candidate/{candidate_id}", response_model=list[EducationResponse])
async def list_education_for_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    res = await db.execute(select(Education).where(Education.candidate_id == candidate_id))
    return res.scalars().all()


@router.delete("/education/{item_id}", status_code=204)
async def delete_education(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Education).where(Education.id == item_id, Education.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    await db.commit()


@router.put("/education/{item_id}", response_model=EducationResponse)
async def update_education(
    item_id: int,
    body: EducationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Education).where(Education.id == item_id, Education.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    for field, value in body.model_dump().items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item


# ── Languages ────────────────────────────────────────────
@router.post("/languages", response_model=LanguageResponse, status_code=201)
async def add_language(
    body: LanguageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    item = Language(candidate_id=cid, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/languages", response_model=list[LanguageResponse])
async def list_languages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Language).where(Language.candidate_id == cid))
    return res.scalars().all()


@router.get("/languages/candidate/{candidate_id}", response_model=list[LanguageResponse])
async def list_languages_for_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    res = await db.execute(select(Language).where(Language.candidate_id == candidate_id))
    return res.scalars().all()


@router.delete("/languages/{item_id}", status_code=204)
async def delete_language(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Language).where(Language.id == item_id, Language.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    await db.commit()


@router.put("/languages/{item_id}", response_model=LanguageResponse)
async def update_language(
    item_id: int,
    body: LanguageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(Language).where(Language.id == item_id, Language.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    for field, value in body.model_dump().items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item


# ── Projects & Certificates ─────────────────────────────
@router.post("/projects", response_model=ProjectCertificateResponse, status_code=201)
async def add_project(
    body: ProjectCertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    item = ProjectCertificate(candidate_id=cid, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/projects", response_model=list[ProjectCertificateResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(ProjectCertificate).where(ProjectCertificate.candidate_id == cid))
    return res.scalars().all()


@router.get("/projects/candidate/{candidate_id}", response_model=list[ProjectCertificateResponse])
async def list_projects_for_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    res = await db.execute(select(ProjectCertificate).where(ProjectCertificate.candidate_id == candidate_id))
    return res.scalars().all()


@router.delete("/projects/{item_id}", status_code=204)
async def delete_project(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(ProjectCertificate).where(ProjectCertificate.id == item_id, ProjectCertificate.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    await db.commit()


@router.put("/projects/{item_id}", response_model=ProjectCertificateResponse)
async def update_project(
    item_id: int,
    body: ProjectCertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    cid = await _get_candidate_id(current_user, db)
    res = await db.execute(select(ProjectCertificate).where(ProjectCertificate.id == item_id, ProjectCertificate.candidate_id == cid))
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    for field, value in body.model_dump().items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item
