from pydantic import BaseModel


class VacancyCreate(BaseModel):
    title: str
    description: str | None = None


class VacancyResponse(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = {"from_attributes": True}
