from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.vacancy import Vacancy
from app.deps import require_role
from app.schemas.vacancy import VacancyCreate, VacancyResponse

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("/", response_model=list[VacancyResponse])
async def list_vacancies(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Vacancy))
    return result.scalars().all()


@router.post("/", response_model=VacancyResponse, status_code=201)
async def create_vacancy(
    body: VacancyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr")),
):
    vacancy = Vacancy(title=body.title, description=body.description)
    db.add(vacancy)
    await db.commit()
    await db.refresh(vacancy)
    return vacancy


@router.delete("/{vacancy_id}", status_code=204)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("hr")),
):
    from fastapi import HTTPException
    result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    await db.delete(vacancy)
    await db.commit()
