"""Emotion API — Text-based tension and confidence analysis.

POST /emotion/analyze     → Analyze a single answer
POST /emotion/batch       → Analyze multiple answers for trends
"""

from fastapi import APIRouter, Query
from typing import List

from services.emotion_analyzer import analyze_tension, batch_analyze

router = APIRouter()


@router.post("/analyze")
async def analyze(text: str = Query(..., min_length=10)):
    """Analyze a single answer for tension and confidence indicators."""
    return analyze_tension(text)


@router.post("/batch")
async def batch(answers: List[str] = Query(...)):
    """Analyze multiple answers for overall tension trends."""
    return batch_analyze(answers)
