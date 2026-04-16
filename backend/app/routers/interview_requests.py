from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.interview_request import InterviewRequest
from app.models.candidate import CandidateProfile
from app.models.application import Application, ApplicationStatus
from app.schemas.interview_request import (
    InterviewRequestCreate, InterviewRequestResponse, InterviewRequestStatusUpdate
)
from app.services.notifications import notify_user, notify_users

router = APIRouter(prefix="/interview-requests", tags=["interview-requests"])


@router.post("/", response_model=InterviewRequestResponse, status_code=201)
async def create_request(
    body: InterviewRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("manager")),
):
    # Verify candidate exists
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.id == body.candidate_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    req = InterviewRequest(
        manager_id=current_user.id,
        candidate_id=body.candidate_id,
        comment=body.comment,
        preferred_format=body.preferred_format,
        preferred_time=body.preferred_time,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    # Notify all HR users about the new request
    hr_res = await db.execute(select(User).where(User.role == UserRole.hr))
    hr_ids = [u.id for u in hr_res.scalars().all()]
    await notify_users(hr_ids, "interview_request_new", {
        "request_id": req.id,
        "candidate_id": req.candidate_id,
        "manager_id": current_user.id,
    })

    return req


@router.get("/", response_model=list[InterviewRequestResponse])
async def list_requests(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "admin")),
):
    """HR sees all pending interview requests from managers."""
    result = await db.execute(
        select(InterviewRequest).order_by(InterviewRequest.created_at.desc())
    )
    return result.scalars().all()


@router.get("/my", response_model=list[InterviewRequestResponse])
async def my_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("manager")),
):
    result = await db.execute(
        select(InterviewRequest)
        .where(InterviewRequest.manager_id == current_user.id)
        .order_by(InterviewRequest.created_at.desc())
    )
    return result.scalars().all()


@router.put("/{req_id}/status", response_model=InterviewRequestResponse)
async def update_request_status(
    req_id: int,
    body: InterviewRequestStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "admin")),
):
    result = await db.execute(
        select(InterviewRequest).where(InterviewRequest.id == req_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if body.status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be accepted or rejected")

    req.status = body.status

    # When accepted: move candidate's latest application to manager_interview
    if body.status == "accepted":
        app_result = await db.execute(
            select(Application)
            .where(Application.candidate_id == req.candidate_id)
            .order_by(Application.id.desc())
        )
        app = app_result.scalars().first()
        if app and app.status not in (
            ApplicationStatus.offer,
            ApplicationStatus.hired,
            ApplicationStatus.rejected,
        ):
            app.status = ApplicationStatus.manager_interview

    await db.commit()
    await db.refresh(req)

    # Notify the manager who made the request
    await notify_user(req.manager_id, "interview_request_updated", {
        "request_id": req.id,
        "status": body.status,
        "candidate_id": req.candidate_id,
    })

    return req
