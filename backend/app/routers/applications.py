from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse, StatusUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=list[ApplicationResponse])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager")),
):
    result = await db.execute(select(Application))
    return result.scalars().all()


@router.get("/my", response_model=list[ApplicationResponse])
async def my_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    profile_result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return []
    result = await db.execute(
        select(Application).where(Application.candidate_id == profile.id)
    )
    return result.scalars().all()


@router.post("/", response_model=ApplicationResponse, status_code=201)
async def create_application(
    body: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your profile first")

    # Check if application already exists
    existing_app = await db.execute(
        select(Application).where(
            Application.candidate_id == profile.id,
            Application.vacancy_id == body.vacancy_id
        )
    )
    if existing_app.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already applied for this vacancy")

    app = Application(candidate_id=profile.id, vacancy_id=body.vacancy_id)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.put("/{app_id}/status", response_model=ApplicationResponse)
async def update_status(
    app_id: int,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr")),
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = body.status
    await db.commit()
    await db.refresh(app)
    return app
