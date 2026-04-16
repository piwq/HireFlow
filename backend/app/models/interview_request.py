from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class InterviewRequest(Base):
    __tablename__ = "interview_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_format: Mapped[str | None] = mapped_column(String(20), nullable=True)  # online/offline/phone
    preferred_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/accepted/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
