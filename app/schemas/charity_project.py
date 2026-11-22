"""Pydantic schemas for charity projects."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CharityProjectBase(BaseModel):
    """Project fields; all optional, unknown fields are rejected."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[int] = Field(None, gt=0)
    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    """Request body for creating a project: all fields required."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    full_amount: int = Field(..., gt=0)


class CharityProjectUpdate(CharityProjectBase):
    """Request body for updating a project: any subset of fields."""


class CharityProjectDB(CharityProjectCreate):
    """Project as returned by the API."""

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
