"""Payment routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.payment import PaymentPublic
from app.services.payments import list_user_payments

router = APIRouter(tags=['payments'])


@router.get('/payments', response_model=list[PaymentPublic], summary='List my payments')
async def list_my_payments(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)) -> list[PaymentPublic]:
    payments = await list_user_payments(db, current_user.id)
    return [PaymentPublic.model_validate(p) for p in payments]
