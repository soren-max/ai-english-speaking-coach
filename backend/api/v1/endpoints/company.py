"""Company API — Simulated company culture interview styles.

GET  /company/list        → List all supported companies
GET  /company/{id}        → Get full company profile
GET  /company/{id}/questions?position=  → Get company-tailored questions
GET  /company/{id}/plan?position=      → Generate full interview plan
"""

from fastapi import APIRouter, HTTPException, Query

from services.company_profiles import (
    list_companies, get_company, get_company_questions, generate_interview_plan,
)

router = APIRouter()


@router.get("/list")
async def companies():
    """List all supported company profiles with summaries."""
    return {"companies": list_companies()}


@router.get("/{company_id}")
async def company_profile(company_id: str):
    """Get full profile for a company."""
    profile = get_company(company_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
    return profile


@router.get("/{company_id}/questions")
async def company_questions(
    company_id: str,
    position: str = Query("Software Engineer"),
    limit: int = Query(5, ge=1, le=20),
):
    """Get interview questions tailored to a company's style."""
    qs = get_company_questions(company_id, position, limit=limit)
    return {
        "company": company_id,
        "position": position,
        "count": len(qs),
        "questions": qs,
    }


@router.get("/{company_id}/plan")
async def interview_plan(
    company_id: str,
    position: str = Query("Software Engineer"),
):
    """Generate a complete mock interview plan for a company + position."""
    plan = generate_interview_plan(company_id, position)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
    return plan
