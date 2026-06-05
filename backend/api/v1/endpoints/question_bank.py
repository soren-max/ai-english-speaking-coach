"""Question Bank API — Curated interview questions + auto-refresh.

GET  /question-bank/{position}   →  Questions for a position
GET  /question-bank/stats        →  Bank statistics
POST /question-bank/refresh      →  Scrape fresh questions from GitHub
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services.question_bank import bank
from services.question_scraper import fetch_from_github

router = APIRouter()


@router.get("/{position}")
async def get_questions(
    position: str,
    topic: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(10, ge=1, le=50),
):
    """Get interview questions for a position.

    Supports filtering by topic and difficulty.
    """
    questions = bank.get_questions(
        position=position,
        topic=topic,
        difficulty=difficulty,
        limit=limit,
    )
    return {
        "position": position,
        "count": len(questions),
        "questions": questions,
    }


@router.get("/stats")
async def get_stats():
    """Get question bank statistics."""
    return bank.get_stats()


@router.post("/refresh")
async def refresh_questions():
    """Scrape fresh interview questions from web sources.

    Fetches from GitHub awesome-lists and public repos.
    Merges new questions into the bank (deduplicates by question text).
    """
    try:
        new_questions = await fetch_from_github()
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch questions: {str(e)}",
        )

    count = bank.refresh(new_questions)

    return {
        "message": f"Added {count} new questions",
        "sources_checked": len(new_questions),
        "total": bank.get_stats()["total_questions"],
    }
