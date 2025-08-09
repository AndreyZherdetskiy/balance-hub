"""Account routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.account import AccountPublic
from app.services.accounts import get_or_create_account, list_user_accounts
from app.services.users import get_user

router = APIRouter(tags=['accounts'])


@router.get('/accounts', response_model=list[AccountPublic], summary='List my accounts')
async def list_my_accounts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)) -> list[AccountPublic]:
    accounts = await list_user_accounts(db, current_user.id)
    return [AccountPublic.model_validate(a) for a in accounts]


@router.get('/admin/users/{user_id}/accounts', response_model=list[AccountPublic], dependencies=[Depends(get_current_admin)], summary='List user accounts (admin)')
async def admin_list_user_accounts(user_id: int, db: AsyncSession = Depends(get_db_session)) -> list[AccountPublic]:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    accounts = await list_user_accounts(db, user_id)
    return [AccountPublic.model_validate(a) for a in accounts]


@router.post('/admin/users/{user_id}/accounts', response_model=AccountPublic, dependencies=[Depends(get_current_admin)], summary='Create account for user (admin)')
async def admin_create_account(user_id: int, db: AsyncSession = Depends(get_db_session)) -> AccountPublic:
    account = await get_or_create_account(db, user_id)
    return AccountPublic.model_validate(account)
