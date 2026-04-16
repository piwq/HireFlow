from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.feedback import Feedback
from app.models.interview import Interview
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.notifications import notify_users

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    body: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("manager", "hr", "admin")),
):
    result = await db.execute(select(Interview).where(Interview.id == body.interview_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Interview not found")

    feedback = Feedback(
        interview_id=body.interview_id,
        manager_id=current_user.id,
        text=body.text,
        score_overall=body.score_overall,
        score_technical=body.score_technical,
        score_communication=body.score_communication,
        score_fit=body.score_fit,
        strengths=body.strengths,
        weaknesses=body.weaknesses,
        recommendation=body.recommendation,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Notify all HR users about new feedback
    hr_res = await db.execute(select(User).where(User.role == UserRole.hr))
    hr_ids = [u.id for u in hr_res.scalars().all()]
    await notify_users(hr_ids, "new_feedback", {
        "feedback_id": feedback.id,
        "interview_id": feedback.interview_id,
        "manager_id": current_user.id,
    })

    return feedback


@router.get("/", response_model=list[FeedbackResponse])
async def list_all_feedbacks(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(select(Feedback).order_by(Feedback.created_at.desc()))
    return result.scalars().all()


@router.get("/interview/{interview_id}", response_model=list[FeedbackResponse])
async def get_feedbacks(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(
        select(Feedback).where(Feedback.interview_id == interview_id)
    )
    return result.scalars().all()
