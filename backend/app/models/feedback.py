from sqlalchemy import ForeignKey, Text, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"))
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Structured feedback fields per ТЗ 4.10
    score_overall: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_technical: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_communication: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_fit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strengths: Mapped[str | None] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)  # recommend/reserve/reject/re_interview

    interview: Mapped["Interview"] = relationship(back_populates="feedbacks")
