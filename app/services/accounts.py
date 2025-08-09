"""Account service operations."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


async def get_or_create_account(db: AsyncSession, user_id: int, account_id: int | None = None) -> Account:
    """Get existing account by id or create a new account for a user."""
    if account_id is not None:
        result = await db.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
        account = result.scalar_one_or_none()
        if account:
            return account
    account = Account(user_id=user_id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def list_user_accounts(db: AsyncSession, user_id: int) -> list[Account]:
    """List accounts for a given user."""
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    return result.scalars().all()


async def apply_balance_change(db: AsyncSession, account: Account, amount: Decimal) -> Account:
    """Apply a balance change to an account."""
    account.balance = (account.balance or Decimal('0.00')) + amount
    await db.commit()
    await db.refresh(account)
    return account
