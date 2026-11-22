"""Pydantic schemas for donations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationBase(BaseModel):
    """Donation fields sent by a user."""

    full_amount: int = Field(..., gt=0)
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    """Request body for making a donation."""


class DonationDB(DonationCreate):
    """Donation as shown to its author."""

    id: int
    create_date: datetime
    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """Donation with investment details, shown to superusers."""

    user_id: Optional[int]
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
