from pydantic import BaseModel
from datetime import datetime


class InterviewCreate(BaseModel):
    application_id: int
    scheduled_at: datetime


class InterviewResponse(BaseModel):
    id: int
    application_id: int
    scheduled_at: datetime
    room_code: str

    model_config = {"from_attributes": True}
