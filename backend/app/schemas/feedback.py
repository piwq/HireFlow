from pydantic import BaseModel
from datetime import datetime


class FeedbackCreate(BaseModel):
    interview_id: int
    text: str


class FeedbackResponse(BaseModel):
    id: int
    interview_id: int
    manager_id: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}
