from pydantic import BaseModel


class ProfileUpsert(BaseModel):
    full_name: str
    skills: str | None = None
    experience: str | None = None
    resume_url: str | None = None
    # Extended fields per ТЗ
    phone: str | None = None
    city: str | None = None
    citizenship: str | None = None
    birth_date: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    desired_position: str | None = None
    specialization: str | None = None
    level: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    employment_type: str | None = None
    work_format: str | None = None
    relocation_ready: bool | None = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    skills: str | None
    experience: str | None
    resume_url: str | None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    citizenship: str | None = None
    birth_date: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    desired_position: str | None = None
    specialization: str | None = None
    level: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    employment_type: str | None = None
    work_format: str | None = None
    relocation_ready: bool | None = None

    model_config = {"from_attributes": True}


class ResumeEnhanceRequest(BaseModel):
    current_experience: str | None = None
    current_skills: str | None = None


class ResumeGenerateRequest(BaseModel):
    answers: list[str]


class ResumeAIResponse(BaseModel):
    enhanced_skills: str
    enhanced_experience: str


class ResumeEnhanceStreamRequest(BaseModel):
    current_content: str
    prompt: str


class DraftSaveRequest(BaseModel):
    content: str


class DraftResponse(BaseModel):
    content: str | None
