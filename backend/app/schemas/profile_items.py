from pydantic import BaseModel


class WorkExperienceCreate(BaseModel):
    company: str
    position: str
    period: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    responsibilities: str | None = None
    achievements: str | None = None
    stack: str | None = None


class WorkExperienceResponse(WorkExperienceCreate):
    id: int
    candidate_id: int
    model_config = {"from_attributes": True}


class EducationCreate(BaseModel):
    institution: str
    faculty: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    degree: str | None = None


class EducationResponse(EducationCreate):
    id: int
    candidate_id: int
    model_config = {"from_attributes": True}


class LanguageCreate(BaseModel):
    name: str
    level: str | None = None


class LanguageResponse(LanguageCreate):
    id: int
    candidate_id: int
    model_config = {"from_attributes": True}


class ProjectCertificateCreate(BaseModel):
    title: str
    description: str | None = None
    date: str | None = None
    url: str | None = None


class ProjectCertificateResponse(ProjectCertificateCreate):
    id: int
    candidate_id: int
    model_config = {"from_attributes": True}
