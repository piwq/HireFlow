from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    doc_type: str
    name: str
    url: str


class DocumentResponse(BaseModel):
    id: int
    candidate_id: int
    doc_type: str
    name: str
    url: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
