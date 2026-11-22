"""Import all models in one place so Alembic sees their tables."""

from app.core.db import Base
from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.models.user import User


__all__ = ['Base', 'CharityProject', 'Donation', 'User']
