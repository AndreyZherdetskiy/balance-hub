"""ORM-модель счёта пользователя."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants.money import MonetaryConstants
from app.db.base import Base
from app.db.types import SafeMoney


if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.user import User


class Account(Base):
    """ORM-модель счёта пользователя с балансом."""

    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    balance: Mapped[Decimal] = mapped_column(
        SafeMoney(), default=MonetaryConstants.ZERO_TWO_PLACES, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="account", cascade="all,delete"
    )
