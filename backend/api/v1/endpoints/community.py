"""Community API — Peer review and answer sharing.

POST /community/share              → Share an interview answer
GET  /community/shares             → Community feed (paginated)
GET  /community/share/{id}         → Share detail + reviews
POST /community/share/{id}/review  → Add a peer review
GET  /community/stats              → Community statistics
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services.community_service import (
    create_share,
    get_feed,
    get_share_detail,
    add_peer_review,
    get_stats,
)

router = APIRouter()


@router.post("/share")
async def share_answer(
    session_id: str = Query(...),
    question: str = Query(...),
    answer: str = Query(...),
    position: str = Query(...),
    is_anonymous: bool = Query(True),
):
    """Share an interview Q&A pair to the community.

    AI automatically evaluates the answer and generates feedback.
    """
    if len(answer.strip()) < 10:
        raise HTTPException(status_code=400, detail="Answer too short (min 10 chars)")
    if len(question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Question too short")

    share = await create_share(
        session_id=session_id,
        question=question,
        answer=answer,
        position=position,
        is_anonymous=is_anonymous,
    )
    return share


@router.get("/shares")
async def list_shares(
    position: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """Get community feed of shared interview answers."""
    return get_feed(position=position, page=page, page_size=page_size)


@router.get("/share/{share_id}")
async def get_share(share_id: str):
    """Get a shared answer with AI review and peer reviews."""
    share = get_share_detail(share_id)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    return share


@router.post("/share/{share_id}/review")
async def add_review(
    share_id: str,
    rating: int = Query(..., ge=1, le=5),
    comment: str = Query(...),
    reviewer_name: str = Query("Anonymous Peer"),
):
    """Add a peer review to a shared answer."""
    if len(comment.strip()) < 5:
        raise HTTPException(status_code=400, detail="Review comment too short")

    review = add_peer_review(
        share_id=share_id,
        rating=rating,
        comment=comment,
        reviewer_name=reviewer_name,
    )
    if not review:
        raise HTTPException(status_code=404, detail="Share not found")
    return review


@router.get("/stats")
async def community_stats():
    """Get community statistics."""
    return get_stats()
