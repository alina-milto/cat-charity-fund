"""Charity project model."""

from sqlalchemy import Column, String, Text

from app.core.abstract import CharityDonationBase


class CharityProject(CharityDonationBase):
    """Fundraising project with a unique name and a description."""

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
