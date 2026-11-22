"""Tests for fixes made during the code review."""

from http import HTTPStatus

import httpx
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.main import app


PROJECT_URL = '/charity_project/{project_id}'
REGISTER_URL = '/auth/register'
REPORT_URL = '/yandex/'


def test_update_project_keeps_its_own_name(superuser_client, charity_project):
    response = superuser_client.patch(
        PROJECT_URL.format(project_id=charity_project.id),
        json={'name': charity_project.name, 'description': 'New text'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['description'] == 'New text'


def test_update_project_with_another_project_name(
    superuser_client, charity_project, charity_project_nunchaku
):
    response = superuser_client.patch(
        PROJECT_URL.format(project_id=charity_project.id),
        json={'name': charity_project_nunchaku.name},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize('password, status', [
    ('short7!', HTTPStatus.BAD_REQUEST),
    ('long-enough', HTTPStatus.CREATED),
])
def test_password_min_length(test_client, password, status):
    response = test_client.post(REGISTER_URL, json={
        'email': 'cat@example.com',
        'password': password,
    })
    assert response.status_code == status


def test_settings_require_secret(monkeypatch):
    monkeypatch.delenv('SECRET', raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_short_secret():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret='too-short')


async def test_yandex_client_requires_async_with():
    client = YandexDiskClient(token='token')
    with pytest.raises(RuntimeError):
        await client.upload_file('https://example.com', b'data')


class BrokenYandexDiskClient:
    """Fake client that fails as if Yandex Disk were unreachable."""

    async def create_excel_file(self, title):
        raise httpx.ConnectError('Yandex Disk is unreachable')


async def broken_yandex_client():
    yield BrokenYandexDiskClient()


def test_report_hides_yandex_disk_errors(
    superuser_client, closed_charity_project
):
    app.dependency_overrides[get_yandex_client] = broken_yandex_client
    try:
        response = superuser_client.post(REPORT_URL)
    finally:
        del app.dependency_overrides[get_yandex_client]
    assert response.status_code == HTTPStatus.BAD_GATEWAY
    detail = response.json()['detail']
    assert 'unreachable' not in detail
    assert detail == 'Yandex Disk is unavailable, please try again later.'
