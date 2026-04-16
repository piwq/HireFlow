from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, union, func as sa_func, case

from app.database import get_db
from app.deps import require_role, get_current_user
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.message import Message
from app.schemas.message import UserListItem

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/telegram-bot-info")
async def telegram_bot_info(current_user: User = Depends(get_current_user)):
    from app.config import settings
    return {
        "bot_username": settings.telegram_bot_username,
        "telegram_linked": bool(current_user.telegram_chat_id),
    }


@router.get("/telegram-link")
async def telegram_link(current_user: User = Depends(get_current_user)):
    from app.config import settings
    from app.services.telegram_bot import generate_link_token
    if not settings.telegram_bot_username:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    token = generate_link_token(current_user.id)
    return {"url": f"https://t.me/{settings.telegram_bot_username}?start={token}"}


@router.get("/", response_model=list[UserListItem])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "manager", "admin")),
):
    # Correct subquery for last message per partner
    sub_q = select(
        sa_func.max(Message.created_at).label("last_at"),
        case(
            (Message.sender_id == current_user.id, Message.receiver_id),
            else_=Message.sender_id
        ).label("partner_id")
    ).where(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).group_by("partner_id").subquery()

    result = await db.execute(
        select(User, CandidateProfile, sub_q.c.last_at)
        .outerjoin(CandidateProfile, User.id == CandidateProfile.user_id)
        .outerjoin(sub_q, User.id == sub_q.c.partner_id)
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
            profile_id=profile.id if profile else None,
            last_message_at=last_at
        )
        for user, profile, last_at in rows
    ]


@router.get("/conversations", response_model=list[UserListItem])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return users who have exchanged messages with the current user."""
    sub_q = select(
        sa_func.max(Message.created_at).label("last_at"),
        case(
            (Message.sender_id == current_user.id, Message.receiver_id),
            else_=Message.sender_id
        ).label("partner_id")
    ).where(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).group_by("partner_id").subquery()

    result = await db.execute(
        select(User, CandidateProfile, sub_q.c.last_at)
        .outerjoin(CandidateProfile, User.id == CandidateProfile.user_id)
        .join(sub_q, User.id == sub_q.c.partner_id)
        .order_by(sub_q.c.last_at.desc())
    )
    rows = result.all()
    return [
        UserListItem(
            id=user.id,
            email=user.email,
            role=user.role.value,
            full_name=profile.full_name if profile else None,
            profile_id=profile.id if profile else None,
            last_message_at=last_at
        )
        for user, profile, last_at in rows
    ]

