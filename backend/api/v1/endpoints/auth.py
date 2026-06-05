from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(*, db: AsyncSession = Depends(get_db), body: UserCreate):
    """Register a new user account."""
    ...


@router.post("/login", response_model=TokenResponse)
async def login(*, db: AsyncSession = Depends(get_db), body: UserLogin):
    """Authenticate and return JWT token."""
    ...


@router.get("/me", response_model=UserResponse)
async def get_me():
    """Get current authenticated user info."""
    ...
