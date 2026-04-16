from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.application import Application
from app.models.status_history import StatusHistory
from app.schemas.application import ApplicationCreate, ApplicationResponse, StatusUpdate
from app.schemas.status_history import StatusHistoryResponse
from app.services.notifications import notify_user

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=list[ApplicationResponse])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
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
    await db.flush()

    # Log initial status
    history = StatusHistory(
        application_id=app.id,
        from_status=None,
        to_status=app.status.value,
        changed_by=current_user.id,
    )
    db.add(history)

    await db.commit()
    await db.refresh(app)

    # Notify HR about new application
    try:
        from app.models.user import User
        from app.models.vacancy import Vacancy
        from app.services.notifications import notify_user
        
        # Get vacancy title for the notification
        vac_res = await db.execute(select(Vacancy.title).where(Vacancy.id == app.vacancy_id))
        vac_title = vac_res.scalar_one_or_none() or "Вакансия"
        
        # Get all HR users
        hr_res = await db.execute(select(User.id).where(User.role == 'hr'))
        hr_ids = [r[0] for r in hr_res.all()]
        
        for hr_id in hr_ids:
            await notify_user(hr_id, "application_new", {
                "application_id": app.id,
                "vacancy_id": app.vacancy_id,
                "vacancy_title": vac_title,
                "candidate_name": profile.full_name or "Кандидат",
            })
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to notify HR about new app: {e}")

    return app


@router.put("/{app_id}/status", response_model=ApplicationResponse)
async def update_status(
    app_id: int,
    body: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_status = app.status.value if app.status else None
    app.status = body.status

    # Log status change
    history = StatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=body.status.value,
        changed_by=current_user.id,
    )
    db.add(history)

    await db.commit()
    await db.refresh(app)

    # Notify candidate about status change
    profile_res = await db.execute(
        select(CandidateProfile).where(CandidateProfile.id == app.candidate_id)
    )
    profile = profile_res.scalar_one_or_none()
    if profile:
        await notify_user(profile.user_id, "application_status", {
            "application_id": app.id,
            "vacancy_id": app.vacancy_id,
            "status": body.status.value,
        })

    return app


@router.get("/{app_id}/history", response_model=list[StatusHistoryResponse])
async def get_status_history(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager", "admin")),
):
    result = await db.execute(
        select(StatusHistory)
        .where(StatusHistory.application_id == app_id)
        .order_by(StatusHistory.changed_at)
    )
    return result.scalars().all()
