from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user, require_role
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.schemas.candidate import ProfileUpsert, ProfileResponse

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=list[ProfileResponse])
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr", "manager")),
):
    result = await db.execute(
        select(CandidateProfile).options(selectinload(CandidateProfile.user))
    )
    profiles = result.scalars().all()
    out = []
    for p in profiles:
        out.append(ProfileResponse(
            id=p.id,
            user_id=p.user_id,
            full_name=p.full_name,
            skills=p.skills,
            experience=p.experience,
            resume_url=p.resume_url,
            email=p.user.email if p.user else None,
        ))
    return out


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        skills=profile.skills,
        experience=profile.experience,
        resume_url=profile.resume_url,
        email=current_user.email,
    )


@router.post("/profile", response_model=ProfileResponse)
async def upsert_profile(
    body: ProfileUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("candidate")),
):
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile:
        profile.full_name = body.full_name
        profile.skills = body.skills
        profile.experience = body.experience
        if body.resume_url:
            profile.resume_url = body.resume_url
    else:
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=body.full_name,
            skills=body.skills,
            experience=body.experience,
            resume_url=body.resume_url,
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.full_name,
        skills=profile.skills,
        experience=profile.experience,
        resume_url=profile.resume_url,
        email=current_user.email,
    )
