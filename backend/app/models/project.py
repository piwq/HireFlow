from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectCertificate(Base):
    __tablename__ = "project_certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="projects")
