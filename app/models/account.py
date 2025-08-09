"""Account ORM model."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    """Represents a user's account with a balance."""

    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped['User'] = relationship('User', back_populates='accounts')
    payments: Mapped[list['Payment']] = relationship('Payment', back_populates='account', cascade='all,delete')
