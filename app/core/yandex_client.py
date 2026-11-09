from http import HTTPStatus
from typing import AsyncGenerator, Optional

import httpx
from fastapi import HTTPException

from app.core.config import settings


BASE_URL = 'https://cloud-api.yandex.net/v1/disk'
REPORTS_FOLDER = 'QRKot Reports'
TIMEOUT = 30.0
EXCEL_MIME_TYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
TOKEN_NOT_SET = 'Интеграция с Яндекс Диском не настроена: токен не задан.'
EMPTY_UPLOAD_URL = 'Яндекс Диск не вернул ссылку для загрузки файла.'
EMPTY_PUBLIC_URL = 'Яндекс Диск не вернул публичную ссылку на файл.'


class YandexDiskClient:

    def __init__(self, token: str) -> None:
        self.token = token
        self.base_url = BASE_URL
        self.headers = {'Authorization': f'OAuth {token}'}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> 'YandexDiskClient':
        self._client = httpx.AsyncClient(timeout=TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _create_folder(self, folder: str = REPORTS_FOLDER) -> None:
        response = await self._client.put(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': f'disk:/{folder}'},
        )
        if response.status_code == HTTPStatus.CONFLICT:
            return
        response.raise_for_status()

    async def create_excel_file(
        self,
        title: str,
        folder: str = REPORTS_FOLDER,
    ) -> tuple[str, str]:
        await self._create_folder(folder)
        file_path = f'disk:/{folder}/{title}'
        response = await self._client.get(
            f'{self.base_url}/resources/upload',
            headers=self.headers,
            params={'path': file_path, 'overwrite': 'true'},
        )
        response.raise_for_status()
        upload_url = response.json().get('href')
        if not upload_url:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=EMPTY_UPLOAD_URL,
            )
        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        response = await self._client.put(
            upload_url,
            content=content,
            headers={'Content-Type': EXCEL_MIME_TYPE},
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        response = await self._client.put(
            f'{self.base_url}/resources/publish',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()
        response = await self._client.get(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()
        public_url = response.json().get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail=EMPTY_PUBLIC_URL,
            )
        return public_url


async def get_yandex_client() -> AsyncGenerator[YandexDiskClient, None]:
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=TOKEN_NOT_SET,
        )
    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
