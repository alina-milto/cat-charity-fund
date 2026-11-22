"""Database engine, session factory and declarative base."""

from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr

from app.core.config import settings


class PreBase:
    """Base for all models: lowercase table name and integer id."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    """Yield a database session for one request."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
