from pydantic import BaseModel
from datetime import datetime


class StatusHistoryResponse(BaseModel):
    id: int
    application_id: int
    from_status: str | None
    to_status: str
    changed_by: int
    changed_at: datetime

    model_config = {"from_attributes": True}
