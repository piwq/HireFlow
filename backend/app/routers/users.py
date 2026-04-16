from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, union

from app.database import get_db
from app.deps import require_role, get_current_user
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.message import Message
from app.schemas.message import UserListItem

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserListItem])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "manager")),
):
    result = await db.execute(
        select(User, CandidateProfile)
        .outerjoin(CandidateProfile, User.id == CandidateProfile.user_id)
        .where(User.id != current_user.id)
        .order_by(User.role, User.email)
    )
    rows = result.all()
    return [
        UserListItem(
            id=user.id,
            email=user.email,
            role=user.role.value,
            full_name=profile.full_name if profile else None,
        )
        for user, profile in rows
    ]


@router.get("/conversations", response_model=list[UserListItem])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return users who have exchanged messages with the current user."""
    # Collect distinct partner IDs from messages
    sent = select(Message.receiver_id.label("partner_id")).where(
        Message.sender_id == current_user.id
    )
    received = select(Message.sender_id.label("partner_id")).where(
        Message.receiver_id == current_user.id
    )
    partner_ids_q = union(sent, received).subquery()

    result = await db.execute(
        select(User, CandidateProfile)
        .outerjoin(CandidateProfile, User.id == CandidateProfile.user_id)
        .where(User.id.in_(select(partner_ids_q.c.partner_id)))
        .order_by(User.role, User.email)
    )
    rows = result.all()
    return [
        UserListItem(
            id=user.id,
            email=user.email,
            role=user.role.value,
            full_name=profile.full_name if profile else None,
        )
        for user, profile in rows
    ]

