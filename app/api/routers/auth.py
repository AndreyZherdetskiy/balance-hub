"""Auth routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import LoginRequest, Token
from app.services.auth import login
from app.db.session import get_db_session

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=Token, summary='Login by email/password')
async def login_route(payload: LoginRequest, db: AsyncSession = Depends(get_db_session)) -> Token:
    """Authenticate and return JWT token."""
    try:
        token = await login(db, payload.email, payload.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return Token(access_token=token)
