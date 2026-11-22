"""Report endpoint: closed projects exported to Yandex Disk."""

import logging
from http import HTTPStatus

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report


PROJECTS_NOT_FOUND = 'No closed projects yet, nothing to report.'
YANDEX_DISK_ERROR = 'Yandex Disk is unavailable, please try again later.'

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary='Create a report on Yandex Disk',
    description=(
        'Builds an Excel report of closed projects sorted by funding '
        'speed, uploads it to Yandex Disk and returns a public link. '
        'Superusers only.'
    ),
)
async def create_report(
    session: AsyncSession = Depends(get_async_session),
    yandex_client: YandexDiskClient = Depends(get_yandex_client),
) -> str:
    """Upload a report of closed projects and return its link."""
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    if not projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECTS_NOT_FOUND,
        )
    try:
        return await create_simple_report(projects, yandex_client)
    except httpx.HTTPError:
        logger.exception('Failed to upload the report to Yandex Disk.')
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail=YANDEX_DISK_ERROR,
        )
