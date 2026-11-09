from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    description: str = 'Сервис для поддержки котиков!'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    yandex_disk_token: Optional[str] = None
    report_format: str = '%Y-%m-%d_%H-%M-%S'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
