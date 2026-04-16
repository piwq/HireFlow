from sqlalchemy import String, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    candidate = "candidate"
    hr = "hr"
    manager = "manager"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.candidate)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    profile: Mapped["CandidateProfile"] = relationship(back_populates="user", uselist=False)
