from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    name: Mapped[str] = mapped_column(String(100))
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    candidate: Mapped["CandidateProfile"] = relationship(back_populates="languages")
