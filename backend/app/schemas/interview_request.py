from pydantic import BaseModel
from datetime import datetime


class InterviewRequestCreate(BaseModel):
    candidate_id: int
    comment: str | None = None
    preferred_format: str | None = None
    preferred_time: str | None = None


class InterviewRequestResponse(BaseModel):
    id: int
    manager_id: int
    candidate_id: int
    comment: str | None
    preferred_format: str | None
    preferred_time: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewRequestStatusUpdate(BaseModel):
    status: str  # accepted/rejected
