"""Strategy API — Retrieves interview strategy analysis for a session.

GET /strategy/{session_id}  →  Strategy analysis JSON
"""

from fastapi import APIRouter, HTTPException

from agents.strategy_store import StrategyStore

router = APIRouter()


@router.get("/{session_id}")
async def get_strategy(session_id: str):
    """Get the interview strategy analysis for a session.

    Returns analysis of STAR completeness, technical depth,
    and project logic with per-answer recommendations.
    """
    store = StrategyStore.get_instance()
    analysis = store.get(session_id)

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No strategy analysis found. Complete at least one interview round first.",
        )

    return analysis
