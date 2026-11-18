"""Authentication setup: JWT backend, user manager and dependencies."""

import logging
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
    schemas,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User


MIN_PASSWORD_LENGTH = 8
logger = logging.getLogger(__name__)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Yield the user database adapter for fastapi-users."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """Return the JWT strategy: tokens signed with the app secret."""
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """User manager with custom password rules and registration log."""

    async def validate_password(
        self,
        password: str,
        user: Union[schemas.UC, User],
    ) -> None:
        """Reject short passwords and passwords containing the email."""
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordException(
                reason=(
                    'Password must be at least '
                    f'{MIN_PASSWORD_LENGTH} characters long.'
                )
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason='Password must not contain your email.'
            )

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ):
        """Log every successful registration."""
        logger.info('User %s registered.', user.email)


async def get_user_manager(user_db=Depends(get_user_db)):
    """Yield the user manager for fastapi-users."""
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
