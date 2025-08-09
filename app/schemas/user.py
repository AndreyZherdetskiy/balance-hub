"""Pydantic schemas for User."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base User fields."""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a user (admin only)."""

    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Schema for updating a user (admin only)."""

    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_admin: bool | None = None


class UserPublic(UserBase):
    """Public User representation."""

    id: int

    class Config:
        from_attributes = True


class UserMe(UserPublic):
    """Current user representation."""

    pass


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = 'bearer'


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str
