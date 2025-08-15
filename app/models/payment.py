"""ORM-модель платежа."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants.field_constraints import FieldConstraints
from app.db.base import Base
from app.db.types import SafeMoney


if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.user import User


class Payment(Base):
    """ORM-модель платежа пополнения счёта пользователя."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(
        String(FieldConstraints.TRANSACTION_ID_MAX_LENGTH),
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(SafeMoney(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="payments")
    account: Mapped["Account"] = relationship("Account", back_populates="payments")
