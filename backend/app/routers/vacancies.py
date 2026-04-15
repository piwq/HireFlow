from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyResponse

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("/", response_model=list[VacancyResponse])
async def list_vacancies(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Vacancy))
    return result.scalars().all()
