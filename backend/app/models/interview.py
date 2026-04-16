from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    room_code: Mapped[str] = mapped_column(String(32))
    format: Mapped[str | None] = mapped_column(String(20), nullable=True)  # online/offline/phone
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    invitation_status: Mapped[str | None] = mapped_column(String(20), nullable=True, default="pending")  # pending/confirmed/declined

    application: Mapped["Application"] = relationship(back_populates="interview")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
