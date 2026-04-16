from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_role
from app.models.user import User, UserRole
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.models.interview import Interview
from app.models.feedback import Feedback
from app.schemas.admin import UserRoleUpdate, UserBlockUpdate, UserAdminResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserAdminResponse])
async def admin_list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return [
        UserAdminResponse(
            id=u.id, email=u.email, role=u.role.value,
            is_blocked=u.is_blocked, telegram_chat_id=u.telegram_chat_id,
        )
        for u in users
    ]


@router.put("/users/{user_id}/role", response_model=UserAdminResponse)
async def admin_update_role(
    user_id: int,
    body: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    if body.role not in ("candidate", "hr", "manager", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = UserRole(body.role)
    await db.commit()
    await db.refresh(user)
    return UserAdminResponse(
        id=user.id, email=user.email, role=user.role.value,
        is_blocked=user.is_blocked, telegram_chat_id=user.telegram_chat_id,
    )


@router.put("/users/{user_id}/block", response_model=UserAdminResponse)
async def admin_block_user(
    user_id: int,
    body: UserBlockUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_blocked = body.is_blocked
    await db.commit()
    await db.refresh(user)
    return UserAdminResponse(
        id=user.id, email=user.email, role=user.role.value,
        is_blocked=user.is_blocked, telegram_chat_id=user.telegram_chat_id,
    )


@router.delete("/users/{user_id}", status_code=204)
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    users_res = await db.execute(select(User))
    users = users_res.scalars().all()

    candidates_res = await db.execute(select(CandidateProfile))
    candidates_count = len(candidates_res.scalars().all())

    apps_res = await db.execute(select(Application))
    apps = apps_res.scalars().all()

    interviews_res = await db.execute(select(Interview))
    interviews_count = len(interviews_res.scalars().all())

    feedbacks_res = await db.execute(select(Feedback))
    feedbacks_count = len(feedbacks_res.scalars().all())

    role_counts = {}
    for u in users:
        role_counts[u.role.value] = role_counts.get(u.role.value, 0) + 1

    status_counts = {}
    for a in apps:
        s = a.status.value
        status_counts[s] = status_counts.get(s, 0) + 1

    return {
        "total_users": len(users),
        "role_counts": role_counts,
        "total_candidates": candidates_count,
        "total_applications": len(apps),
        "status_counts": status_counts,
        "total_interviews": interviews_count,
        "total_feedbacks": feedbacks_count,
        "blocked_users": sum(1 for u in users if u.is_blocked),
    }
