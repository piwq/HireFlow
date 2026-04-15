from sqlalchemy import ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    new = "new"
    screening = "screening"
    interview = "interview"
    hired = "hired"
    rejected = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"))
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus), default=ApplicationStatus.new
    )

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="applications")
    vacancy: Mapped["Vacancy"] = relationship(back_populates="applications")
    interview: Mapped["Interview"] = relationship(back_populates="application", uselist=False)
