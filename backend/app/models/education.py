from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    institution: Mapped[str] = mapped_column(String(255))
    faculty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(100), nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="educations")
