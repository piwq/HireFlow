from pydantic import BaseModel
from datetime import datetime


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    text: str
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    id: int
    email: str
    role: str
    full_name: str | None = None
    profile_id: int | None = None
    last_message_at: datetime | None = None
