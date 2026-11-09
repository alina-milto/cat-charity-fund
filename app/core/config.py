"""Application settings loaded from environment variables and .env."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


MIN_SECRET_LENGTH = 32


class Settings(BaseSettings):
    """Application settings.

    ``secret`` has no default: the app refuses to start without it,
    so JWT tokens are never signed with a publicly known key.
    """

    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    description: str = 'Сервис для поддержки котиков!'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = Field(min_length=MIN_SECRET_LENGTH)
    yandex_disk_token: Optional[str] = None
    report_format: str = '%Y-%m-%d_%H-%M-%S'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
