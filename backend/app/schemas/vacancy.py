from pydantic import BaseModel


class VacancyResponse(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = {"from_attributes": True}
