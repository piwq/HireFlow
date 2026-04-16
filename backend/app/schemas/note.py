from pydantic import BaseModel
from datetime import datetime


class NoteCreate(BaseModel):
    candidate_id: int
    text: str


class NoteResponse(BaseModel):
    id: int
    candidate_id: int
    author_id: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}
