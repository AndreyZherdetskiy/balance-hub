"""User-related routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import UserCreate, UserMe, UserPublic, UserUpdate
from app.services.users import create_user, delete_user, get_user, list_users, update_user

router = APIRouter(tags=['users'])


@router.get('/users/me', response_model=UserMe, summary='Get current user profile')
async def read_me(current_user: User = Depends(get_current_user)) -> UserMe:
    """Return current user data."""
    return UserMe.model_validate(current_user)


@router.post('/admin/users', response_model=UserPublic, dependencies=[Depends(get_current_admin)], summary='Create user (admin)')
async def admin_create_user(payload: UserCreate, db: AsyncSession = Depends(get_db_session)) -> UserPublic:
    user = await create_user(db, payload.email, payload.full_name, payload.password, is_admin=payload.is_admin)
    return UserPublic.model_validate(user)


@router.get('/admin/users', response_model=list[UserPublic], dependencies=[Depends(get_current_admin)], summary='List users (admin)')
async def admin_list_users(db: AsyncSession = Depends(get_db_session)) -> list[UserPublic]:
    users = await list_users(db)
    return [UserPublic.model_validate(u) for u in users]


@router.get('/admin/users/{user_id}', response_model=UserPublic, dependencies=[Depends(get_current_admin)], summary='Get user by id (admin)')
async def admin_get_user(user_id: int, db: AsyncSession = Depends(get_db_session)) -> UserPublic:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return UserPublic.model_validate(user)


@router.patch('/admin/users/{user_id}', response_model=UserPublic, dependencies=[Depends(get_current_admin)], summary='Update user (admin)')
async def admin_update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db_session)) -> UserPublic:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user = await update_user(db, user, email=payload.email, full_name=payload.full_name, password=payload.password, is_admin=payload.is_admin)
    return UserPublic.model_validate(user)


@router.delete('/admin/users/{user_id}', dependencies=[Depends(get_current_admin)], summary='Delete user (admin)')
async def admin_delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)) -> dict:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    await delete_user(db, user)
    return {'status': 'ok'}
