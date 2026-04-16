from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.database import get_db
from app.deps import require_role
from app.models.user import User
from app.models.interview import Interview
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.schemas.interview import InterviewCreate, InterviewResponse

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewResponse, status_code=201)
async def create_interview(
    body: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager")),
):
    room_code = uuid4().hex[:12]
    interview = Interview(
        application_id=body.application_id,
        scheduled_at=body.scheduled_at,
        room_code=room_code,
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/my", response_model=list[InterviewResponse])
async def my_interviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    profile_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = profile_res.scalar_one_or_none()
    if not profile:
        return []
    app_ids_res = await db.execute(
        select(Application.id).where(Application.candidate_id == profile.id)
    )
    app_ids = [row[0] for row in app_ids_res.fetchall()]
    if not app_ids:
        return []
    interviews_res = await db.execute(
        select(Interview).where(Interview.application_id.in_(app_ids))
    )
    return interviews_res.scalars().all()


@router.get("/", response_model=list[InterviewResponse])
async def list_interviews(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager")),
):
    result = await db.execute(select(Interview))
    return result.scalars().all()
