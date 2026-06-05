from fastapi import APIRouter

from api.v1.endpoints import auth, interview, health, correction, strategy, growth, question_bank, community, emotion, i18n, company

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(interview.router, prefix="/session", tags=["Interview Session"])
api_v1_router.include_router(correction.router, prefix="/correction", tags=["Correction"])
api_v1_router.include_router(strategy.router, prefix="/strategy", tags=["Strategy"])
api_v1_router.include_router(growth.router, prefix="/growth", tags=["Growth"])
api_v1_router.include_router(question_bank.router, prefix="/question-bank", tags=["Question Bank"])
api_v1_router.include_router(community.router, prefix="/community", tags=["Community"])
api_v1_router.include_router(emotion.router, prefix="/emotion", tags=["Emotion"])
api_v1_router.include_router(i18n.router, prefix="/i18n", tags=["I18n"])
api_v1_router.include_router(company.router, prefix="/company", tags=["Company"])
