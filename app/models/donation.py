from sqlalchemy import Column, ForeignKey, Integer, Text

from app.core.abstract import CharityDonationBase


class Donation(CharityDonationBase):
    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
