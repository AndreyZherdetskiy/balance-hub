"""Pydantic schemas for Account."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class AccountBase(BaseModel):
    """Base account fields."""

    balance: Decimal


class AccountCreate(BaseModel):
    """Schema for creating an account (admin or webhook)."""

    user_id: int


class AccountPublic(AccountBase):
    """Public representation of an account."""

    id: int
    user_id: int

    class Config:
        from_attributes = True
