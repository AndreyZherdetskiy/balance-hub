"""ORM-модель пользователя приложения (обычный или администратор)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants.field_constraints import FieldConstraints
from app.db.base import Base


if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.payment import Payment


class User(Base):
    """ORM-модель пользователя приложения (обычный или администратор)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(FieldConstraints.USER_EMAIL_MAX_LENGTH),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(FieldConstraints.USER_FULL_NAME_MAX_LENGTH), nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(FieldConstraints.HASHED_PASSWORD_MAX_LENGTH), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="user", cascade="all,delete"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user", cascade="all,delete"
    )
