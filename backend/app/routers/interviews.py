from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.database import get_db
from app.deps import require_role
from app.models.user import User
from app.models.interview import Interview
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


@router.get("/", response_model=list[InterviewResponse])
async def list_interviews(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager")),
):
    result = await db.execute(select(Interview))
    return result.scalars().all()
