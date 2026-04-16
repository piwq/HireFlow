from pydantic import BaseModel


class UserRoleUpdate(BaseModel):
    role: str  # candidate/hr/manager/admin


class UserBlockUpdate(BaseModel):
    is_blocked: bool


class UserAdminResponse(BaseModel):
    id: int
    email: str
    role: str
    is_blocked: bool
    telegram_chat_id: str | None = None

    model_config = {"from_attributes": True}
