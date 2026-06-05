"""I18n API — Multi-language support for international users.

GET  /i18n/term?term=       → Translate an interview term to Chinese
GET  /i18n/stage/{n}        → Get interview stage hints in Chinese
GET  /i18n/hint?question=   → Generate Chinese hint for a question
GET  /i18n/company/{name}   → Get interview tips for a specific company
"""

from fastapi import APIRouter, Query

from services.i18n_service import (
    translate_term, get_stage_hint, hint_for_question,
    get_company_tip, list_supported_companies, translate_phrase,
)

router = APIRouter()


@router.get("/term")
async def lookup_term(term: str = Query(...)):
    """Translate an interview term to Chinese."""
    zh = translate_term(term)
    return {"term": term, "chinese": zh, "found": zh is not None}


@router.get("/stage/{stage}")
async def stage_hint(stage: int):
    """Get Chinese hints for an interview stage (1-5)."""
    hints = get_stage_hint(stage)
    if not hints:
        return {"error": "Stage must be 1-5"}, 404
    return hints


@router.get("/hint")
async def question_hint(question: str = Query(...)):
    """Generate a Chinese strategy hint for any interview question."""
    zh = hint_for_question(question)
    phrase_zh = translate_phrase(question)
    return {
        "question": question,
        "strategy_hint": zh,
        "phrase_hint": phrase_zh,
    }


@router.get("/companies")
async def supported_companies():
    """List companies with available interview tips."""
    return {"companies": list_supported_companies()}


@router.get("/company/{name}")
async def company_tips(name: str):
    """Get interview tips for a specific company."""
    tips = get_company_tip(name)
    if not tips:
        return {"error": f"No tips for {name}. Supported: {list_supported_companies()}"}, 404
    return {"company": name, **tips}
