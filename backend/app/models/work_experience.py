from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    company: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(255))
    period: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    achievements: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack: Mapped[str | None] = mapped_column(Text, nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="work_experiences")
