from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from schemas.interview import (
    SessionStartRequest,
    SessionStartResponse,
    SessionMessageRequest,
    SessionMessageResponse,
    SessionEndResponse,
    InterviewSessionDetailResponse,
)
from services.interview_service import InterviewService

router = APIRouter()


def _get_service(db: AsyncSession = Depends(get_db)) -> InterviewService:
    return InterviewService(db)


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    body: SessionStartRequest,
    service: InterviewService = Depends(_get_service),
):
    """Start a new interview session for a given position.

    Creates the session, generates the first AI question, and returns both.
    """
    try:
        result = await service.create_session(
            position=body.position, resume_text=body.resume_text
        )
        return SessionStartResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=SessionMessageResponse)
async def send_message(
    body: SessionMessageRequest,
    service: InterviewService = Depends(_get_service),
):
    """Send a message in an interview session and get AI reply."""
    try:
        result = await service.send_message(
            session_id=str(body.session_id),
            content=body.content,
        )
        return SessionMessageResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end", response_model=SessionEndResponse)
async def end_session(
    body: SessionMessageRequest,
    service: InterviewService = Depends(_get_service),
):
    """End an interview session and generate the report.

    Accepts a final message from the user before ending.
    Uses SessionMessageRequest body (session_id + content).
    """
    try:
        # If there's a final message, save it first
        if body.content.strip():
            await service.send_message(
                session_id=str(body.session_id),
                content=body.content,
            )
        result = await service.end_session(session_id=str(body.session_id))
        return SessionEndResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=InterviewSessionDetailResponse)
async def get_session(
    session_id: UUID,
    service: InterviewService = Depends(_get_service),
):
    """Get full session details including conversations and report."""
    result = await service.get_session(session_id=str(session_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return InterviewSessionDetailResponse(**result)


@router.get("/{session_id}/star")
async def get_star_analysis(
    session_id: UUID,
    service: InterviewService = Depends(_get_service),
):
    """Extract STAR method examples from interview conversation."""
    result = await service.get_session(session_id=str(session_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")

    convs = result["conversations"]
    history = [
        {"role": c["role"], "content": c["content"]}
        for c in convs
    ]
    stars = await service.reporter.analyze_star(history)
    return stars


@router.get("/{session_id}/errors")
async def get_error_analysis(
    session_id: UUID,
    service: InterviewService = Depends(_get_service),
):
    """Analyze language errors and improvement opportunities."""
    result = await service.get_session(session_id=str(session_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")

    convs = result["conversations"]
    history = [
        {"role": c["role"], "content": c["content"]}
        for c in convs
    ]
    errors = await service.reporter.analyze_errors(history)
    return errors
