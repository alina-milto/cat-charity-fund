"""Client for uploading files to Yandex Disk."""

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
TOKEN_NOT_SET = 'Yandex Disk integration is not configured: no token set.'
EMPTY_UPLOAD_URL = 'Yandex Disk did not return an upload link.'
EMPTY_PUBLIC_URL = 'Yandex Disk did not return a public link to the file.'
CLIENT_NOT_OPEN = (
    'YandexDiskClient must be used as "async with YandexDiskClient(...)".'
)


class YandexDiskClient:
    """Async client for the Yandex Disk REST API.

    Use it as an async context manager: the HTTP connection is opened
    on enter and closed on exit.
    """

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
            await self.client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Return the open HTTP client.

        Raises RuntimeError if the client is used outside ``async with``.
        """
        if self._client is None:
            raise RuntimeError(CLIENT_NOT_OPEN)
        return self._client

    async def _create_folder(self, folder: str = REPORTS_FOLDER) -> None:
        """Create the folder on the disk; do nothing if it exists."""
        response = await self.client.put(
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
        """Reserve a file on the disk.

        Returns the URL to upload the file content to and the file path.
        """
        await self._create_folder(folder)
        file_path = f'disk:/{folder}/{title}'
        response = await self.client.get(
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
        """Upload the file content to the reserved upload URL."""
        response = await self.client.put(
            upload_url,
            content=content,
            headers={'Content-Type': EXCEL_MIME_TYPE},
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        """Make the file public and return its public URL."""
        response = await self.client.put(
            f'{self.base_url}/resources/publish',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()
        response = await self.client.get(
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
    """Yield a Yandex Disk client; respond 503 if no token is set."""
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=TOKEN_NOT_SET,
        )
    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
