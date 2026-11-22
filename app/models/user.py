"""User model."""

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """User account managed by fastapi-users, with an integer id."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
