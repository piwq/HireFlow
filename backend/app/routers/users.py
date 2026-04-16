from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
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
