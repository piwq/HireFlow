from pydantic import BaseModel
from datetime import datetime


class FeedbackCreate(BaseModel):
    interview_id: int
    text: str
    score_overall: int | None = None
    score_technical: int | None = None
    score_communication: int | None = None
    score_fit: int | None = None
    strengths: str | None = None
    weaknesses: str | None = None
    recommendation: str | None = None  # recommend/reserve/reject/re_interview


class FeedbackResponse(BaseModel):
    id: int
    interview_id: int
    manager_id: int
    text: str
    created_at: datetime
    score_overall: int | None = None
    score_technical: int | None = None
    score_communication: int | None = None
    score_fit: int | None = None
    strengths: str | None = None
    weaknesses: str | None = None
    recommendation: str | None = None

    model_config = {"from_attributes": True}
