from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    room_code: Mapped[str] = mapped_column(String(32))

    application: Mapped["Application"] = relationship(back_populates="interview")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="interview")
