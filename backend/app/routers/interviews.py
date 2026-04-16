from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.interview import Interview
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewUpdate, InvitationStatusUpdate
from app.services.notifications import notify_user

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewResponse, status_code=201)
async def create_interview(
    body: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    # Check if interview already exists
    existing_res = await db.execute(select(Interview).where(Interview.application_id == body.application_id))
    existing_interview = existing_res.scalar_one_or_none()

    _room_code = uuid4().hex
    room_code = _room_code[:12]
    
    if existing_interview:
        # Update existing
        existing_interview.scheduled_at = body.scheduled_at
        existing_interview.room_code = room_code
        existing_interview.format = body.format
        existing_interview.location = body.location
        existing_interview.comment = body.comment
        existing_interview.manager_id = body.manager_id
        existing_interview.invitation_status = "pending"
        interview = existing_interview
    else:
        # Create new
        interview = Interview(
            application_id=body.application_id,
            scheduled_at=body.scheduled_at,
            room_code=room_code,
            format=body.format,
            location=body.location,
            comment=body.comment,
            manager_id=body.manager_id,
        )
        db.add(interview)
    
    await db.commit()
    await db.refresh(interview)

    # Notify candidate
    app_res = await db.execute(select(Application).where(Application.id == body.application_id))
    app = app_res.scalar_one_or_none()
    if app:
        profile_res = await db.execute(
            select(CandidateProfile).where(CandidateProfile.id == app.candidate_id)
        )
        profile = profile_res.scalar_one_or_none()
        if profile:
            await notify_user(profile.user_id, "interview_scheduled", {
                "interview_id": interview.id,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "format": interview.format,
                "room_code": interview.room_code,
            })

    # Notify assigned manager
    if interview.manager_id:
        await notify_user(interview.manager_id, "interview_assigned", {
            "interview_id": interview.id,
            "scheduled_at": interview.scheduled_at.isoformat(),
            "room_code": interview.room_code,
        })

    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    body: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "admin")),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    old_time = interview.scheduled_at

    if body.scheduled_at is not None:
        interview.scheduled_at = body.scheduled_at
    if body.format is not None:
        interview.format = body.format
    if body.location is not None:
        interview.location = body.location
    if body.comment is not None:
        interview.comment = body.comment
    if body.manager_id is not None:
        interview.manager_id = body.manager_id

    await db.commit()
    await db.refresh(interview)

    # Notify about time change
    if body.scheduled_at and body.scheduled_at != old_time:
        app_res = await db.execute(select(Application).where(Application.id == interview.application_id))
        app = app_res.scalar_one_or_none()
        if app:
            profile_res = await db.execute(
                select(CandidateProfile).where(CandidateProfile.id == app.candidate_id)
            )
            profile = profile_res.scalar_one_or_none()
            if profile:
                await notify_user(profile.user_id, "interview_rescheduled", {
                    "interview_id": interview.id,
                    "scheduled_at": interview.scheduled_at.isoformat(),
                    "room_code": interview.room_code,
                })
        if interview.manager_id:
            await notify_user(interview.manager_id, "interview_rescheduled", {
                "interview_id": interview.id,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "room_code": interview.room_code,
            })

    return interview


@router.delete("/{interview_id}", status_code=204)
async def cancel_interview(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "admin")),
):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Notify participants about cancellation
    app_res = await db.execute(select(Application).where(Application.id == interview.application_id))
    app = app_res.scalar_one_or_none()
    if app:
        profile_res = await db.execute(
            select(CandidateProfile).where(CandidateProfile.id == app.candidate_id)
        )
        profile = profile_res.scalar_one_or_none()
        if profile:
            await notify_user(profile.user_id, "interview_cancelled", {
                "interview_id": interview.id,
            })
    if interview.manager_id:
        await notify_user(interview.manager_id, "interview_cancelled", {
            "interview_id": interview.id,
        })

    await db.delete(interview)
    await db.commit()


@router.put("/{interview_id}/invitation", response_model=InterviewResponse)
async def update_invitation_status(
    interview_id: int,
    body: InvitationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Candidate or manager can confirm/decline their interview."""
    if body.status not in ("confirmed", "declined"):
        raise HTTPException(status_code=400, detail="Status must be confirmed or declined")

    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.invitation_status = body.status
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
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(select(Interview))
    return result.scalars().all()
