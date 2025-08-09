"""FastAPI dependencies: DB session, auth, and rate limiting."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db_session
from app.models.user import User
from sqlalchemy import select


settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


async def get_current_user(db: AsyncSession = Depends(get_db_session), token: str = Depends(oauth2_scheme)) -> User:
    """Resolve current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        subject: str | None = payload.get('sub')
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin privileges required')
    return user
