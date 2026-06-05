import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from models.base import UUIDMixin


class SessionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConversationRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class InterviewSession(UUIDMixin, Base):
    __tablename__ = "interview_sessions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    position: Mapped[str] = mapped_column(String(200), nullable=False, comment="Target position, e.g. 'Software Engineer'")
    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(SessionStatus, name="session_status"),
        default=SessionStatus.PENDING,
        nullable=False,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    overall_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversations = relationship(
        "Conversation", back_populates="session", cascade="all, delete-orphan",
        order_by="Conversation.created_at"
    )
    report = relationship(
        "Report", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )


class Conversation(UUIDMixin, Base):
    __tablename__ = "conversations"

    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, index=True
    )
    role: Mapped[ConversationRole] = mapped_column(
        SAEnum(ConversationRole, name="conversation_role"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session = relationship("InterviewSession", back_populates="conversations")


class Report(UUIDMixin, Base):
    __tablename__ = "reports"

    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=False, unique=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fluency: Mapped[float] = mapped_column(Float, nullable=False)
    grammar: Mapped[float] = mapped_column(Float, nullable=False)
    vocabulary: Mapped[float] = mapped_column(Float, nullable=False)
    communication: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]", comment="JSON array of strengths"
    )
    weaknesses: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]", comment="JSON array of weaknesses"
    )
    suggestions: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]", comment="JSON array of suggestions"
    )

    session = relationship("InterviewSession", back_populates="report")
