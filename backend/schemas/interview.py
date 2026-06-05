from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# ──────────────────────────────
# Session Start
# ──────────────────────────────

class SessionStartRequest(BaseModel):
    position: str
    resume_text: str = ""


class SessionStartResponse(BaseModel):
    session_id: UUID
    question: str


# ──────────────────────────────
# Session Message
# ──────────────────────────────

class SessionMessageRequest(BaseModel):
    session_id: UUID
    content: str


class SessionMessageResponse(BaseModel):
    reply: str


# ──────────────────────────────
# Session End
# ──────────────────────────────

class SessionEndResponse(BaseModel):
    session_id: UUID
    report: "ReportResponse"


# ──────────────────────────────
# InterviewSession
# ──────────────────────────────

class InterviewSessionCreate(BaseModel):
    position: str


class InterviewSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    position: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_score: Optional[float] = None

    model_config = {"from_attributes": True}


class InterviewSessionListResponse(BaseModel):
    items: list[InterviewSessionResponse]
    total: int


# ──────────────────────────────
# Conversation
# ──────────────────────────────

class ConversationCreate(BaseModel):
    role: str
    content: str


class ConversationResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────
# Report
# ──────────────────────────────

class ReportResponse(BaseModel):
    id: UUID
    session_id: UUID
    overall_score: float
    fluency: float
    grammar: float
    vocabulary: float
    communication: float
    summary: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    overall_score: float
    fluency: float
    grammar: float
    vocabulary: float
    communication: float
    summary: str
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []


# ──────────────────────────────
# InterviewSession detail
# ──────────────────────────────

class InterviewSessionDetailResponse(InterviewSessionResponse):
    conversations: list[ConversationResponse] = []
    report: Optional[ReportResponse] = None
