from pydantic import BaseModel
from datetime import datetime


class InterviewCreate(BaseModel):
    application_id: int
    scheduled_at: datetime
    format: str | None = None  # online/offline/phone
    location: str | None = None
    comment: str | None = None
    manager_id: int | None = None


class InterviewUpdate(BaseModel):
    scheduled_at: datetime | None = None
    format: str | None = None
    location: str | None = None
    comment: str | None = None
    manager_id: int | None = None


class InvitationStatusUpdate(BaseModel):
    status: str  # confirmed/declined


class InterviewResponse(BaseModel):
    id: int
    application_id: int
    scheduled_at: datetime
    room_code: str
    format: str | None = None
    location: str | None = None
    comment: str | None = None
    manager_id: int | None = None
    invitation_status: str | None = None

    model_config = {"from_attributes": True}
