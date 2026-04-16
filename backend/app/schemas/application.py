from pydantic import BaseModel
from datetime import datetime
from app.models.application import ApplicationStatus


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    vacancy_id: int
    status: ApplicationStatus
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationCreate(BaseModel):
    vacancy_id: int
