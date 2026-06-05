"""Growth API — Historical score tracking for growth curves.

GET /growth/history  →  Returns score history for the demo user
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from services.growth_service import get_growth_history, get_demo_user_id

router = APIRouter()


@router.get("/history")
async def get_growth_history_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Get historical interview scores for growth curve visualization.

    Returns scores ordered by date, one entry per completed interview.
    Currently uses demo user; replace with real auth when available.
    """
    user_id = await get_demo_user_id(db)
    if not user_id:
        raise HTTPException(status_code=404, detail="Demo user not found. Complete an interview first.")

    history = await get_growth_history(db, user_id)
    return {
        "history": history,
        "total_sessions": len(history),
    }
