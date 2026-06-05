"""GrowthService — Queries historical interview scores to build growth curves.

Reads from existing reports + interview_sessions tables.
No new tables, no schema changes.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.interview import Report, InterviewSession
from models.user import User


async def get_growth_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Fetch historical scores for a user, ordered by session date.

    Each entry contains the report scores + session metadata.
    Returns empty list if no data.
    """
    # Join reports with interview_sessions to get dates + positions
    query = (
        select(
            Report.overall_score,
            Report.fluency,
            Report.grammar,
            Report.vocabulary,
            Report.communication,
            InterviewSession.start_time,
            InterviewSession.position,
        )
        .join(InterviewSession, Report.session_id == InterviewSession.id)
        .where(InterviewSession.user_id == user_id)
        .where(InterviewSession.status == "completed")
        .order_by(InterviewSession.start_time.asc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    history = []
    for row in rows:
        start_time: datetime = row.start_time
        history.append({
            "date": start_time.strftime("%Y-%m-%d"),
            "position": row.position,
            "overall_score": round(row.overall_score, 1),
            "fluency": round(row.fluency, 1),
            "grammar": round(row.grammar, 1),
            "vocabulary": round(row.vocabulary, 1),
            "communication": round(row.communication, 1),
        })

    return history


async def get_demo_user_id(db: AsyncSession) -> Optional[str]:
    """Get the demo user ID (fallback when no real auth)."""
    result = await db.execute(
        select(User.id).where(User.email == "demo@interviewgpt.dev")
    )
    user = result.scalar_one_or_none()
    if user:
        return str(user)
    return None
