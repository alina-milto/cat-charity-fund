"""Pydantic schemas for users (fastapi-users)."""

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """User as returned by the API."""


class UserCreate(schemas.BaseUserCreate):
    """Request body for registration."""


class UserUpdate(schemas.BaseUserUpdate):
    """Request body for updating a user."""
