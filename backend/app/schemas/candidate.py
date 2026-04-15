from pydantic import BaseModel


class ProfileUpsert(BaseModel):
    full_name: str
    skills: str | None = None
    experience: str | None = None
    resume_url: str | None = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    skills: str | None
    experience: str | None
    resume_url: str | None
    email: str | None = None

    model_config = {"from_attributes": True}
