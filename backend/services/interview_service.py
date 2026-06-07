"""InterviewService v2 — now powered by LangGraph multi-agent workflow.

Coordinates DB operations with the agent graph for:
  start: resume_agent → interviewer_agent
  message: evaluation_agent → follow_up_agent
  end: report_agent
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.interview import (
    InterviewSession,
    SessionStatus,
    Conversation,
    ConversationRole,
    Report,
)
from agents.state import InterviewState


# ── Demo user fallback (no real auth yet) ──
DEMO_USER_EMAIL = "demo@interviewgpt.dev"
DEMO_USER_USERNAME = "demo"


async def _get_or_create_demo_user(db: AsyncSession) -> uuid.UUID:
    from models.user import User
    from core.security import hash_password

    result = await db.execute(
        select(User).where(User.email == DEMO_USER_EMAIL)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=DEMO_USER_EMAIL,
            username=DEMO_USER_USERNAME,
            hashed_password=hash_password("demo"),
        )
        db.add(user)
        await db.flush()

    return user.id


def _report_to_dict(r: Report) -> dict:
    return {
        "id": str(r.id),
        "session_id": str(r.session_id),
        "overall_score": r.overall_score,
        "fluency": r.fluency,
        "grammar": r.grammar,
        "vocabulary": r.vocabulary,
        "communication": r.communication,
        "summary": r.summary,
        "strengths": json.loads(r.strengths) if isinstance(r.strengths, str) else r.strengths,
        "weaknesses": json.loads(r.weaknesses) if isinstance(r.weaknesses, str) else r.weaknesses,
        "suggestions": json.loads(r.suggestions) if isinstance(r.suggestions, str) else r.suggestions,
    }


def _load_conversations(db_convs) -> list[dict]:
    """Load conversation records from DB into message dicts."""
    return [
        {"role": c.role.value, "content": c.content}
        for c in db_convs
    ]


class InterviewService:
    """InterviewGPT v2 — LangGraph-powered interview service."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(
        self, position: str, resume_text: str = ""
    ) -> dict:
        """Create session + run start_graph (resume → interviewer).

        Returns dict with session_id and question.
        """
        user_id = await _get_or_create_demo_user(self.db)

        session = InterviewSession(
            user_id=user_id,
            position=position,
            status=SessionStatus.IN_PROGRESS,
        )
        self.db.add(session)
        await self.db.flush()

        # Run LangGraph: resume_agent → interviewer_agent
        from agents.workflow import start_graph

        initial_state: InterviewState = {
            "resume_text": resume_text,
            "resume_data": None,
            "position": position,
            "session_id": str(session.id),
            "conversation_history": [],
            "current_question": "",
            "current_answer": "",
            "evaluations": [],
            "iteration": 0,
            "max_iterations": 20,
            "final_report": None,
            "error": None,
        }

        result = await start_graph.ainvoke(initial_state)

        first_question = result.get("current_question", "")
        history = result.get("conversation_history", [])

        # Save AI's first message to DB
        if first_question:
            conv = Conversation(
                session_id=session.id,
                role=ConversationRole.ASSISTANT,
                content=first_question,
            )
            self.db.add(conv)
            await self.db.flush()

        return {
            "session_id": str(session.id),
            "question": first_question,
        }

    async def send_message(self, session_id: str, content: str) -> dict:
        """Save user message + run message_graph (evaluation → follow_up).

        Returns dict with reply (the next question/response).
        """
        sid = uuid.UUID(session_id)

        # Save user message to DB
        user_conv = Conversation(
            session_id=sid,
            role=ConversationRole.USER,
            content=content,
        )
        self.db.add(user_conv)

        # Load full conversation + session from DB
        db_session = await self.db.execute(
            select(InterviewSession).where(InterviewSession.id == sid)
        )
        session = db_session.scalar_one_or_none()
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        db_convs = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == sid)
            .order_by(Conversation.created_at)
        )
        conversations = db_convs.scalars().all()
        history = _load_conversations(conversations)

        # Load previous evaluations from Report if exists
        db_report = await self.db.execute(
            select(Report).where(Report.session_id == sid)
        )
        existing_report = db_report.scalar_one_or_none()

        # Build state for message_graph
        # Find the last assistant message (the question being answered)
        last_question = ""
        for msg in reversed(history):
            if msg["role"] == "assistant":
                last_question = msg["content"]
                break

        state: InterviewState = {
            "resume_text": "",
            "resume_data": None,
            "position": session.position,
            "session_id": session_id,
            "conversation_history": history,
            "current_question": last_question,
            "current_answer": content,
            "evaluations": [],
            "iteration": len([m for m in history if m["role"] == "user"]),
            "max_iterations": 20,
            "final_report": None,
            "error": None,
        }

        # Run message_graph
        from agents.workflow import message_graph

        result = await message_graph.ainvoke(state)

        follow_up = result.get("current_question", "")
        updated_history = result.get("conversation_history", [])

        # Save AI response to DB
        if follow_up:
            ai_conv = Conversation(
                session_id=sid,
                role=ConversationRole.ASSISTANT,
                content=follow_up,
            )
            self.db.add(ai_conv)
            await self.db.flush()

        return {"reply": follow_up}

    async def end_session(self, session_id: str) -> dict:
        """End session + run end_graph (report_agent).

        Returns dict with session_id and report.
        """
        sid = uuid.UUID(session_id)

        # Load session
        db_session = await self.db.execute(
            select(InterviewSession).where(InterviewSession.id == sid)
        )
        session = db_session.scalar_one_or_none()
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        # Load conversations
        db_convs = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == sid)
            .order_by(Conversation.created_at)
        )
        conversations = db_convs.scalars().all()
        history = _load_conversations(conversations)

        # Load any existing evaluations (we stored them in report or can regenerate)
        # For now, generate fresh report via end_graph
        state: InterviewState = {
            "resume_text": "",
            "resume_data": None,
            "position": session.position,
            "session_id": session_id,
            "conversation_history": history,
            "current_question": "",
            "current_answer": "",
            "evaluations": [],
            "iteration": len([m for m in history if m["role"] == "user"]),
            "max_iterations": 20,
            "final_report": None,
            "error": None,
        }

        from agents.workflow import end_graph

        result = await end_graph.ainvoke(state)
        report_data = result.get("report", {}) or result.get("final_report", {})

        # Save report to DB
        report = Report(
            session_id=sid,
            overall_score=report_data.get("overall_score", 0),
            fluency=report_data.get("fluency", 0),
            grammar=report_data.get("grammar", 0),
            vocabulary=report_data.get("vocabulary", 0),
            communication=report_data.get("communication", 0),
            summary=report_data.get("summary", ""),
            strengths=json.dumps(report_data.get("strengths", [])),
            weaknesses=json.dumps(report_data.get("weaknesses", [])),
            suggestions=json.dumps(report_data.get("suggestions", [])),
        )
        self.db.add(report)

        # Mark session as completed
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.now(timezone.utc)
        session.overall_score = report.overall_score
        await self.db.flush()

        return {
            "session_id": str(session.id),
            "report": _report_to_dict(report),
        }

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get full session details with conversations and report."""
        sid = uuid.UUID(session_id)

        result = await self.db.execute(
            select(InterviewSession).where(InterviewSession.id == sid)
        )
        session = result.scalar_one_or_none()
        if session is None:
            return None

        conv_result = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == sid)
            .order_by(Conversation.created_at)
        )
        conversations = conv_result.scalars().all()

        report_result = await self.db.execute(
            select(Report).where(Report.session_id == sid)
        )
        report = report_result.scalar_one_or_none()

        return {
            "id": str(session.id),
            "user_id": str(session.user_id),
            "position": session.position,
            "status": session.status.value,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "overall_score": session.overall_score,
            "conversations": [
                {
                    "id": str(c.id),
                    "session_id": str(c.session_id),
                    "role": c.role.value,
                    "content": c.content,
                    "created_at": c.created_at.isoformat(),
                }
                for c in conversations
            ],
            "report": _report_to_dict(report) if report else None,
        }
